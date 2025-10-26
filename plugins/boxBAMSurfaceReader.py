import io
import vtk
import tarfile
import zstandard

from paraview import util
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid
from vtkmodules.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtkmodules.numpy_interface import dataset_adapter as dsa
from paraview.util.vtkAlgorithm import smdomain, smhint, smproperty, smproxy


def set_timesteps(algorithm, timesteps):
    executive = algorithm.GetExecutive()
    outInfo = executive.GetOutputInformation(0)

    outInfo.Remove(executive.TIME_STEPS())
    for timestep in timesteps:
        outInfo.Append(executive.TIME_STEPS(), timestep)

    outInfo.Remove(executive.TIME_RANGE())
    outInfo.Append(executive.TIME_RANGE(), timesteps[0])
    outInfo.Append(executive.TIME_RANGE(), timesteps[-1])


def get_timestep(algorithm):
    executive = algorithm.GetExecutive()
    outInfo = executive.GetOutputInformation(0)
    if not outInfo.Has(executive.UPDATE_TIME_STEP()):
        return 0.0
    timestep = outInfo.Get(executive.UPDATE_TIME_STEP())
    return timestep

def parse_bam_header(header):
    # Format:
    # Apparent Horizon 0, time=1696.0
    t = float(header.split("time=", 1)[1])
    d = {
        "varname": "ah",
        "time": t,
    }
    return d

@smproxy.reader(
    name="boxBAMSurfaceReader",
    label="boxBAMSurfaceReader",
    extensions="box",
    file_description="box with BAM VTK surface files",
)
class boxBAMSurfaceReader(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(
            self,
            nInputPorts=0,
            nOutputPorts=1,
            outputType="vtkUnstructuredGrid",
        )
        self.members = []
        self._timesteps = []
        self._level_suffix = None

    @smproperty.stringvector(name="FileName")
    @smdomain.filelist()
    @smhint.filechooser(extensions="box", file_description="box files")
    def SetFileName(self, value):
        self._filename = value
        self.Modified()

    @smproperty.doublevector(
        name="TimestepValues",
        information_only="1",
        si_class="vtkSITimeStepsProperty",
    )
    def GetTimestepValues(self):
        timesteps = self._timesteps
        return timesteps.tolist() if timesteps is not None else None


    def RequestInformation(self, request, inInfo, outInfo):
        if self._filename is None:
            return

        self.tar = tarfile.open(self._filename)
        members = self.tar.getmembers()
        self.members = []
        n_skip = None
        for i, member in enumerate(members):
            if n_skip is not None:
                if i%n_skip != 0:
                    continue
            self.members += [member]

            # Header
            file_compressed = self.tar.extractfile(member)
            decompressor = zstandard.ZstdDecompressor()
            with io.TextIOWrapper(decompressor.stream_reader(file_compressed), encoding='ascii', errors='ignore') as file:
                file.readline()
                header_str = file.readline().rstrip()
                header = parse_bam_header(header_str)
                self._timesteps += [header["time"]]
            file_compressed.close()

        set_timesteps(self, self._timesteps)

        return 1


    def RequestData(self, request, inInfo, outInfo):
        output = dsa.WrapDataObject(vtkUnstructuredGrid.GetData(outInfo))

        time = get_timestep(self)
        try:
            i = self._timesteps.index(time)
        except:
            return -1
        member = self.members[i]
        decompressor = zstandard.ZstdDecompressor()
        file_content = decompressor.stream_reader(self.tar.extractfile(member)).read()

        reader = vtk.vtkUnstructuredGridReader()
        reader.ReadFromInputStringOn()
        reader.ReadAllScalarsOn()
        reader.ReadAllVectorsOn()
        reader.ReadAllFieldsOn()
        reader.ReadAllColorScalarsOn()
        reader.ReadAllTensorsOn()
        reader.ReadAllTCoordsOn()
        reader.SetBinaryInputString(file_content, len(file_content))
        reader.Update()
        output.ShallowCopy(reader.GetOutput())
        output.Modified()

        return 1