# Import necessary Abaqus modules and constants
from abaqus import *
from abaqusConstants import *
import regionToolset
import sketch
import part
import material
import section
import time
import step
import mesh
import assembly

# Initialize model dictionary and temporary variables
dict_model_beam = {}
temp_var = None

# Function to create and rename the Abaqus model
def NameOfModel(Name=''):
    global temp_var
    # Initialize viewport without displaying any objects
    session.viewports['Viewport: 1'].setValues(displayedObject=None)
    
    # Rename the default model and store in dictionary
    mdb.models.changeKey(fromName='Model-1', toName=Name + 'Beam')
    temp_var = Name + 'Model'
    dict_model_beam[temp_var] = mdb.models[Name + 'Beam']

# Initialize model with a specific name
NameOfModel(Name='SimplySupportedBeam')

# Material properties for concrete
MOE_concrete = 26925  # Modulus of Elasticity (MPa)
density_of_concrete = 2.50E-05  # Density (kg/mm^3)

# Function to define beam dimensions, material properties, and cross-section
def beam_size(width, depth, length, cover, point_load_distance):
    global Part_beam, beam_width, beam_depth, beam_length, beam_cover, locationofload
    
    # Set beam dimensions and load location
    beam_width, beam_depth, beam_length, beam_cover = width, depth, length, cover
    locationofload = point_load_distance

    # Define cross-section sketch for beam
    Sketch_beam = dict_model_beam[temp_var].ConstrainedSketch(name='Beam Cross Section', sheetSize=5)
    Sketch_beam.rectangle(point1=(0, 0), point2=(beam_width, beam_depth))

    # Create beam part as a 3D deformable body and extrude the sketch
    Part_beam = dict_model_beam[temp_var].Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    Part_beam.BaseSolidExtrude(sketch=Sketch_beam, depth=beam_length)

    # Define concrete material with density and elastic properties
    Materialbeam = dict_model_beam[temp_var].Material(name='concretebeam')
    Materialbeam.Density(table=((density_of_concrete,),))
    Materialbeam.Elastic(table=((MOE_concrete, 0.2),))

    # Define concrete damaged plasticity and hardening/damage parameters
    Materialbeam.ConcreteDamagedPlasticity(table=((36.0, 0.1, 1.16, 0.667, 0.0),))
    Materialbeam.concreteDamagedPlasticity.ConcreteCompressionHardening(
        table=((11.6, 0), (14, 1.753e-5), (17, 5.28e-5), (20, 0.0001086),
               (23, 0.0001964), (26, 0.0003463), (29, 0.000873), 
               (25, 0.001771), (20, 0.002337), (15, 0.002807), (10, 0.00323))
    )
    Materialbeam.concreteDamagedPlasticity.ConcreteCompressionDamage(
        table=((0, 0), (0, 1.753e-5), (0, 5.28e-5), (0, 0.0001086), 
               (0, 0.0001964), (0, 0.0003463), (0, 0.000873), 
               (0.1379, 0.001771), (0.3103, 0.002337), 
               (0.4828, 0.002807), (0.6552, 0.00323))
    )
    Materialbeam.concreteDamagedPlasticity.ConcreteTensionStiffening(
        table=((3.3, 0), (2.46, 0.000289), (1.3, 0.0007029), (0.06, 0.0013443))
    )
    Materialbeam.concreteDamagedPlasticity.ConcreteTensionDamage(
        table=((0.0, 0), (0.2545, 0.000289), (0.6061, 0.000703), 
               (0.9818, 0.0013443))
    )

    # Define and assign section properties for the beam
    SectionBeam = dict_model_beam[temp_var].HomogeneousSolidSection(name='concrete_beam', material='concretebeam')
    region_of_beam = Part_beam.cells  # Define region as beam cells
    Part_beam.Set(cells=region_of_beam, name='beam_set')  # Create region set
    Part_beam.SectionAssignment(region=Part_beam.sets['beam_set'], sectionName='concrete_beam')

    # Add datum planes for load positioning
    offsets = [locationofload - 32.5, locationofload, locationofload + 32.5,
               beam_length - 2 * (locationofload + 65) + (locationofload + 65 - 32.5),
               beam_length - 2 * (locationofload + 65) + (locationofload + 65),
               beam_length - 2 * (locationofload + 65) + (locationofload + 65 + 32.5)]
    for offset in offsets:
        Part_beam.DatumPlaneByPrincipalPlane(offset=offset, principalPlane=XYPLANE)

# Define beam with specific parameters
beam_size(width=150, depth=150, length=1300, cover=25, point_load_distance=450)

# Define the distance for point load on the beam
point_load_distance = 450

# Set up the assembly environment

Assembly = dict_model_beam[temp_var].rootAssembly
Assembly.DatumCsysByDefault(CARTESIAN)

# Create an instance of the beam in the assembly
Instance_beam = Assembly.Instance(name='beam Instance', part=Part_beam, dependent=OFF)

# Function to define the plate properties, material, section assignment, and instances
def platesize(plate_depth, plate_length, spacing_from_edge):
    global Instance_Plate, Instance_Plate1, platedepth, platelength
    platedepth = plate_depth
    platelength = plate_length

    # Define the cross-section sketch for the plate
    Sketch_plate = dict_model_beam[temp_var].ConstrainedSketch(name='Plate Cross Section', sheetSize=5)
    Sketch_plate.rectangle(point1=(0, 0), point2=(beam_width, -plate_depth))

    # Create the plate part and extrude the sketch to form a 3D plate
    Part_plate = dict_model_beam[temp_var].Part(name='Plate', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    Part_plate.BaseSolidExtrude(sketch=Sketch_plate, depth=plate_length)

    # Add a datum plane at the center of the plate and partition the cell by this plane
    Part_plate.DatumPlaneByPrincipalPlane(offset=plate_length / 2, principalPlane=XYPLANE)
    Part_plate.PartitionCellByDatumPlane(cells=Part_plate.cells, datumPlane=Part_plate.datums[2])

    # Define material and section properties for the plate
    MaterialPlate = dict_model_beam[temp_var].Material(name='steelplate')
    MaterialPlate.Density(table=((7.58E-05,),))
    MaterialPlate.Elastic(table=((2.1E5, 0.3),))
    MaterialPlate.Plastic(table=((515, 0),))
    SectionPlate = dict_model_beam[temp_var].HomogeneousSolidSection(name='steel_plate', material='steelplate')

    # Assign the section to the plate and create a region set for it
    region_of_Plate = Part_plate.cells
    Part_plate.Set(cells=region_of_Plate, name='bottom_plate')
    Part_plate.SectionAssignment(region=Part_plate.sets['bottom_plate'], sectionName='steel_plate')

    # Create an instance of the plate in the assembly
    Instance_Plate = Assembly.Instance(name='Plate Instance', part=Part_plate, dependent=OFF)
    Assembly.translate(instanceList=('Plate Instance',), vector=(0.0, 0.0, spacing_from_edge))

    # Pattern the plate instance along the length of the beam
    Assembly.LinearInstancePattern(direction1=(0, 0.0, 1.0), direction2=(0.0, 1.0, 0.0), 
                                   instanceList=('Plate Instance',), number1=2, number2=1, 
                                   spacing1=beam_length - plate_length - 2 * spacing_from_edge, 
                                   spacing2=beam_depth + plate_depth)

    # Define the top plate using a similar procedure to the bottom plate
    Sketch_plate1 = dict_model_beam[temp_var].ConstrainedSketch(name='Plate Cross Section 1', sheetSize=5)
    Sketch_plate1.rectangle(point1=(0, beam_depth), point2=(beam_width, beam_depth + plate_depth))
    
    Part_plate1 = dict_model_beam[temp_var].Part(name='Plate1', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    Part_plate1.BaseSolidExtrude(sketch=Sketch_plate1, depth=plate_length)

    # Define material properties and section for the top plate
    MaterialPlate1 = dict_model_beam[temp_var].Material(name='steelplate1')
    MaterialPlate1.Density(table=((7.58E-05,),))
    MaterialPlate1.Elastic(table=((2.1E5, 0.3),))
    MaterialPlate1.Plastic(table=((515, 0),))
    SectionPlate1 = dict_model_beam[temp_var].HomogeneousSolidSection(name='steel_plate_1', material='steelplate1')

    # Assign section to the top plate and create a region set
    region_of_Plate1 = Part_plate1.cells
    Part_plate1.Set(cells=region_of_Plate1, name='top_plate')
    Part_plate1.SectionAssignment(region=Part_plate1.sets['top_plate'], sectionName='steel_plate_1')

    # Instance and position the top plate in the assembly
    Instance_Plate1 = Assembly.Instance(name='Plate Instance 1', part=Part_plate1, dependent=OFF)
    Assembly.translate(instanceList=('Plate Instance 1',), vector=(0.0, 0.0, locationofload - (plate_length / 2)))

    # Calculate midspan distance and pattern the top plate instances
    midspan = beam_length - 2 * locationofload
    Assembly.LinearInstancePattern(direction1=(0, 0.0, 1.0), direction2=(0.0, 1.0, 0.0),
                                   instanceList=('Plate Instance 1',), number1=2, number2=1, 
                                   spacing1=midspan, spacing2=beam_depth + plate_depth)

# Define plate parameters and call the platesize function
platesize(plate_depth=10, plate_length=40, spacing_from_edge=30)

# Define dictionaries for rebar and stirrup sketches, parts, and instances
Sketch_bars = {}
Part_bars = {}
Sketch_bars_top = {}
Part_bars_top = {}
Instance_bottom_bars = {}
Instance_top_bars = {}
inner_width = beam_width - (2 * beam_cover)
Sketch_stirrups = {}
Part_stirrups = {}
Instance_stirrups = {}

# Material and section dictionaries for different rebars and stirrups
materialrebars = {}
materialrebarsbottom = {}
secionrebar_top = {}
materialstirrups = {}
Section_stirrup = {}

# Function to create and place reinforcement bars and stirrups
def total_bar_numbers(no_of_bottom_bars, no_of_top_bars, diameter_of_bottom_bars, diameter_of_top_bars, Dia_of_stirrups, spacing_of_stirrups, end_distance_of_stirrups_from_bar_edge):
    global beam_cover
    temp_iter_index = beam_cover
    edge_dis = end_distance_of_stirrups_from_bar_edge
    no_of_stirrups = (beam_length - 2 * end_distance_of_stirrups_from_bar_edge) / spacing_of_stirrups
    temp_iter_index2 = edge_dis

    # Bottom bar creation loop
    for i in range(no_of_bottom_bars):
        bottom_bar_spacing = inner_width - diameter_of_bottom_bars / (no_of_bottom_bars - 1)
        temp_var1 = f'Sketch_rbar{i}'
        temp_var2 = f'Part_bar{i}'

        # Create sketch for each bottom rebar
        Sketch_bars[temp_var1] = dict_model_beam[temp_var].ConstrainedSketch(name=f'bottom_rebarcrosssection{i}', sheetSize=5)
        Sketch_bars[temp_var1].CircleByCenterPerimeter(center=(0, 0), point1=(1.25, -5.0))

        # Define bottom rebar part and extrude it
        Part_bars[temp_var2] = dict_model_beam[temp_var].Part(name=f'bottomrebar{i}', dimensionality=THREE_D, type=DEFORMABLE_BODY)
        Part_bars[temp_var2].BaseSolidExtrude(sketch=Sketch_bars[temp_var1], depth=beam_length)

        # Create instance of bottom rebar in the assembly
        temp_var5 = f'bottom_instance{i}'
        Instance_bottom_bars[temp_var5] = Assembly.Instance(name=f'bottom_bar_Instance{i}', part=Part_bars[temp_var2], dependent=OFF)
        Assembly.translate(instanceList=(f'bottom_bar_Instance{i}',), vector=(temp_iter_index + (diameter_of_bottom_bars / 2), (diameter_of_bottom_bars / 2 + beam_cover), 0))
        temp_iter_index += bottom_bar_spacing

        # Define material and section properties for bottom rebar
        materialrebarbottom_temp = f'bottom_rebar{i}'
        secionrebar_bottom_temp = f'secionrebar_bottom{i}'
        materialrebarsbottom[materialrebarbottom_temp] = dict_model_beam[temp_var].Material(name=f'bottomrebar{i}')
        materialrebarsbottom[materialrebarbottom_temp].Density(table=((7.58E-05,),))
        materialrebarsbottom[materialrebarbottom_temp].Elastic(table=((2.1E05, 0.3),))
        materialrebarsbottom[materialrebarbottom_temp].Plastic(table=((515, 0),))
        secionrebar_top[secionrebar_bottom_temp] = dict_model_beam[temp_var].HomogeneousSolidSection(name=f'reinforcement_long_bottom{i}', material=f'bottomrebar{i}')

        # Assign section to the bottom rebar
        bottom_bar_set_region = Part_bars[temp_var2].cells
        Part_bars[temp_var2].Set(cells=bottom_bar_set_region, name=f'bottom_rebar{i}')
        Part_bars[temp_var2].SectionAssignment(region=Part_bars[temp_var2].sets[f'bottom_rebar{i}'], sectionName=f'reinforcement_long_bottom{i}')

    time.sleep(0.5)  # Short delay between bar creation

    # Top bar creation loop
    temp_iter_index1 = beam_cover
    for i in range(no_of_top_bars):
        top_bar_spacing = inner_width - diameter_of_top_bars / (no_of_top_bars - 1)
        temp_var3 = f'Sketch_rbar_top{i}'
        temp_var4 = f'Part_bar_top{i}'

        # Create sketch for each top rebar
        Sketch_bars_top[temp_var3] = dict_model_beam[temp_var].ConstrainedSketch(name=f'Top_rebarcrosssection{i}', sheetSize=5)
        Sketch_bars_top[temp_var3].CircleByCenterPerimeter(center=(0, 0), point1=(1.25, -5.0))

        # Define top rebar part and extrude it
        Part_bars[temp_var4] = dict_model_beam[temp_var].Part(name=f'Toprebar{i}', dimensionality=THREE_D, type=DEFORMABLE_BODY)
        Part_bars[temp_var4].BaseSolidExtrude(sketch=Sketch_bars_top[temp_var3], depth=beam_length)

        # Create instance of top rebar in the assembly
        temp_var6 = f'top_instance{i}'
        Instance_top_bars[temp_var6] = Assembly.Instance(name=f'top_bar_Instance{i}', part=Part_bars[temp_var4], dependent=OFF)
        Assembly.translate(instanceList=(f'top_bar_Instance{i}',), vector=(temp_iter_index1 + (diameter_of_top_bars / 2), (beam_depth - beam_cover - diameter_of_top_bars / 2), 0))
        temp_iter_index1 += top_bar_spacing

        # Define material and section properties for top rebar
        materialrebar_temp = f'top_rebar{i}'
        secionrebar_top_temp = f'secionrebar_top{i}'
        materialrebars[materialrebar_temp] = dict_model_beam[temp_var].Material(name=f'toprebar{i}')
        materialrebars[materialrebar_temp].Density(table=((7.58E-05,),))
        materialrebars[materialrebar_temp].Elastic(table=((2.1E05, 0.3),))
        materialrebars[materialrebar_temp].Plastic(table=((450, 0),))
        secionrebar_top[secionrebar_top_temp] = dict_model_beam[temp_var].HomogeneousSolidSection(name=f'reinforcement_long{i}', material=f'toprebar{i}')

        # Assign section to the top rebar
        top_bar_set_region = Part_bars[temp_var4].cells
        Part_bars[temp_var4].Set(cells=top_bar_set_region, name=f'Top_rebar{i}')
        Part_bars[temp_var4].SectionAssignment(region=Part_bars[temp_var4].sets[f'Top_rebar{i}'], sectionName=f'reinforcement_long{i}')

    # Stirrups creation loop
    temp_iter_index2 = edge_dis
    for i in range(int(no_of_stirrups) + 1):
        temp_var7 = f'Sketch_stirrups{i}'
        temp_var8 = f'Part_stirrups{i}'

        # Create sketch and part for stirrups
        Sketch_stirrups[temp_var7] = dict_model_beam[temp_var].ConstrainedSketch(name=f'Stirrups cross section{i}', sheetSize=5)
        Sketch_stirrups[temp_var7].rectangle(point1=(beam_cover, beam_cover), point2=(beam_width - beam_cover, beam_depth - beam_cover))
        Part_stirrups[temp_var8] = dict_model_beam[temp_var].Part(name=f'stir{i}', dimensionality=THREE_D, type=DEFORMABLE_BODY)
        Part_stirrups[temp_var8].BaseWire(sketch=Sketch_stirrups[temp_var7])

        # Rounding edges of stirrups at vertices
        Part_stirrups[temp_var8].Round(radius=diameter_of_top_bars / 2, vertexList=(Part_stirrups[temp_var8].vertices[2], Part_stirrups[temp_var8].vertices[3]))
        Part_stirrups[temp_var8].Round(radius=diameter_of_bottom_bars / 2, vertexList=(Part_stirrups[temp_var8].vertices[0], Part_stirrups[temp_var8].vertices[1]))

        # Set edges for stirrup and create an instance in the assembly
        Stirrup_set_edges = Part_stirrups[temp_var8].edges
        Part_stirrups[temp_var8].Set(edges=Stirrup_set_edges, name=f'Main_part_Stirrup{i}')
        temp_var9 = f'Bar_Stirrup_Instance{i}'
        Instance_stirrups[temp_var9] = Assembly.Instance(name=f'stirrup_Instance{i}', part=Part_stirrups[temp_var8], dependent=OFF)
        Assembly.translate(instanceList=(f'stirrup_Instance{i}',), vector=(0.0, 0.0, temp_iter_index2))
        temp_iter_index2 += spacing_of_stirrups

        # Define material and section properties for stirrups
        materialstirrup_temp = f'stir{i}'
        Sectiostirrup_temp = f'stirrup{i}'
        materialstirrups[materialstirrup_temp] = dict_model_beam[temp_var].Material(name=f'stirrups{i}')
        materialstirrups[materialstirrup_temp].Density(table=((7.58E-05,),))
        materialstirrups[materialstirrup_temp].Elastic(table=((2.1E5, 0.3),))
        Section_stirrup[Sectiostirrup_temp] = dict_model_beam[temp_var].TrussSection(name=f'Londitudinal_stirrups{i}', material=f'stirrups{i}', area=Dia_of_stirrups**2 * 0.785)

        # Assign section to stirrup
        Part_stirrups[temp_var8].SectionAssignment(region=Part_stirrups[temp_var8].sets[f'Main_part_Stirrup{i}'], sectionName=f'Londitudinal_stirrups{i}', offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, thicknessAssignment=FROM_SECTION)

# Execute the function to create bars and stirrups with specified parameters
total_bar_numbers(2, 2, 12, 10, 8, 80, 50)

# Cut and clean up instances for further analysis
Assembly.InstanceFromBooleanCut(cuttingInstances=(Assembly.instances['bottom_bar_Instance0'], Assembly.instances['bottom_bar_Instance1'], Assembly.instances['top_bar_Instance0'], Assembly.instances['top_bar_Instance1']), instanceToBeCut=Assembly.instances['beam Instance'], name='hollow concrete', originalInstances=SUPPRESS)

# Step creation for dynamic analysis
dict_model_beam[temp_var].ExplicitDynamicsStep(name='Step-1', previous='Initial')
dict_model_beam[temp_var].fieldOutputRequests['F-Output-1'].setValues(numIntervals=25, variables=('S', 'SVAVG', 'MISES', 'PE', 'PEVAVG', 'PEEQ', 'PEEQVAVG', 'LE', 'U', 'V', 'A', 'RF', 'RT', 'CSTRESS', 'DAMAGEC', 'DAMAGET', 'EVF'))

# Clean up and finalize model
del Assembly.features['beam Instance']
del dict_model_beam[temp_var].parts['Beam']
Assembly.resumeFeatures(('bottom_bar_Instance0', 'bottom_bar_Instance1', 'top_bar_Instance0', 'top_bar_Instance1'))
Assembly.makeIndependent(instances=(Assembly.instances['hollow concrete-1'],))
