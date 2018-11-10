#! /usr/bin/env python
# -*- coding: latin-1; -*-

# vtk functions to load & save XML VTK and RAW images, cast images


import vtk
import sys, os
    
def castImage(image, coding='uchar'):
    caster = vtk.vtkImageCast()
    caster.SetInput(image)
    if coding=="uchar":
        caster.SetOutputScalarTypeToUnsignedChar()
    elif coding=="ushort":
        caster.SetOutputScalarTypeToUnsignedShort()
    elif coding=="char":
        caster.SetOutputScalarTypeToChar()
    elif coding=="short":
        caster.SetOutputScalarTypeToShort()
    elif coding=="double":
        caster.SetOutputScalarTypeToDouble()
    else:
        print 'bad cast : %s' % coding
    #caster.ClampOverflowOn()
    caster.Update()
    return caster.GetOutput()

def convert16to8bits(name16, name8, extent=(0,255,0,255,0,59)):
    import struct
    l=(extent[1]-extent[0]+1)*(extent[3]-extent[2]+1)*(extent[5]-extent[4]+1)
    typeDataIn=str(l)+'H' # unsigned short
    typeDataOut=str(l)+'B' # unsigned char

    # read file
    file = open(name16, 'rb')
    allfile = file.read()
    file.close()

    # convert file
    outfile = open(name8, 'wb')

    sizIn  = struct.calcsize(typeDataIn)
    sizOut = struct.calcsize(typeDataOut)

    start=0
    value = struct.unpack(typeDataIn, allfile[start:start+sizIn])
    value = (typeDataOut,)+value
    outfile.write(struct.pack(*value))
    outfile.close()
    
def loadRawImage(name, extent=(0,255,0,255,0,59), spacing=(1,1,1), coding='uchar',byteorder='little'):
    """
    load a Raw Image (.img,.raw) into a vtkImageData
    """
    print "load raw",name
    print extent[0],extent[1],extent[2],extent[3],extent[4],extent[5]
    print spacing[0],spacing[1],spacing[2]
    print coding
    print byteorder
    reader = vtk.vtkImageReader()
    reader.SetDataExtent(*extent)
    reader.SetDataSpacing(*spacing)
    
    import os, stat
    if stat.S_ISDIR(os.stat(name)[stat.ST_MODE]):
        reader.SetFilePrefix(name)
        reader.SetFilePattern ("%s/I.%03d")
    else:    
        reader.SetFileDimensionality(3)
        reader.SetFileName(name) # !! pas d'espace dans le nom de fichier !!
        print "setfiledim ",3
    if byteorder=='little':
        reader.SetDataByteOrderToLittleEndian()
    else:
        reader.SetDataByteOrderToBigEndian()
    if coding=='uchar':
        reader.SetDataScalarTypeToUnsignedChar()
    elif coding=='ushort':
        reader.SetDataScalarTypeToUnsignedShort()
    else:
        print 'bad coding : %s' % coding
        sys.exit(1)
    print "update:"
    reader.Update()
    return reader.GetOutput()

def loadNRRDImage(filename):
    import imagingTools
    inFile = open(filename, 'r')
    tag = inFile.readline()
    if tag[0:8]!='NRRD0004':
        print "bad format!"
        sys.exit()
    line = inFile.readline().split()
    while line[0] != 'type:' :
        line = inFile.readline().split()
    coding = line[1]
    print "coding", coding
    while line[0] != 'dimension:':
        line = inFile.readline().split()
    dimensionality = int(line[1])
    print "dimensionality", dimensionality
    while line[0] != 'space:':
        line = inFile.readline().split()     
    space = line[1]
    print "space", space
    while line[0] != 'sizes:':
        line = inFile.readline().split()     
    dimensions = ( int(line[1]),int(line[2]),int(line[3]) )
    print "dimensions", dimensions
    while line[0] != 'space':
        line = inFile.readline().split()    
    directionX = line[2]
    directionY = line[3]
    directionZ = line[4]
    directionX = directionX[1:(len(directionX))-1].rsplit(',',3)
    directionY = directionY[1:(len(directionY))-1].rsplit(',',3)
    directionZ = directionZ[1:(len(directionZ))-1].rsplit(',',3)
    spacing = [0,0,0]
    ordering = []
    for i in range(3):
        if directionX[i] != '0':
            spacing[0] = float(directionX[i])
            ordering.append(0)
        elif directionY[i] != '0':
            spacing[1] = float(directionY[i])
            ordering.append(1)    
        else:
            spacing[2] = float(directionZ[i])
            ordering.append(2)
    for i in range(3):
        if spacing[i] < 0:
            spacing[i] = - spacing[i]
    print "spacing", spacing
    while line[0] != 'endian:':
        line = inFile.readline().split()  
    byteorder = line[1]
    print "byteorder", byteorder
    while line[0] != 'space':
        line = inFile.readline().split()    
    originStr =  line[2]
    originSpl = originStr[1:(len(originStr))-1].rsplit(',',3)
    origin = [float(originSpl[0]),float(originSpl[1]),float(originSpl[2])]
    print "origin", origin
    print "ordering", ordering
    if (space == "left-posterior-superior") or (space == "LPS"):
        origin[1] = -origin[1]
    
    reader = vtk.vtkImageReader2()
    reader.SetDataExtent((0,dimensions[0]-1,0,dimensions[1]-1,0,dimensions[2]-1))
#    reader.SetDataDimensions(dimensions)
    reader.SetDataOrigin(origin)
    reader.SetDataSpacing([spacing[0],spacing[1],spacing[2]])  
    reader.SetFileDimensionality(dimensionality)
    filenameSp = filename.rsplit('.',2) # pas d'espaces ni de point dans le num du fichier!
    if filenameSp[1] == "nhdr":
        reader.SetFileName(filenameSp[0]+'.raw')
    else:
        reader.SetFileName(filename)
    if byteorder=='little':
        reader.SetDataByteOrderToLittleEndian()
    else:
        reader.SetDataByteOrderToBigEndian()
    if coding=='uchar':
        reader.SetDataScalarTypeToUnsignedChar()
    elif coding=='char':
        reader.SetDataScalarTypeToUnsignedChar()
    elif coding=='ushort':
        reader.SetDataScalarTypeToUnsignedShort()
    elif coding=='short':
        reader.SetDataScalarTypeToUnsignedShort()
    elif coding=='float':
        reader.SetDataScalarTypeToFloat()
    else:
        reader.SetDataScalarTypeToDouble()
    reader.Update()
    im = reader.GetOutput()
    return im
    
def saveTiffImage(name, image, coding='uchar'):
    """
    save a Raw Image (.img,.raw) from a vtkImageData
    """
    imgCast = castImage(image, coding)
    writer = vtk.vtkTIFFWriter()
    writer.SetFileName(name)
    writer.SetInput(imgCast)
    writer.SetFileDimensionality(3)
    writer.Write()
    
def saveRawImage(name, image, coding='uchar'):
    """
    save a Raw Image (.img,.raw) from a vtkImageData
    """
    
    imgCast = castImage(image, coding)
    writer = vtk.vtkImageWriter()
    writer.SetFileName(name)
    writer.SetInput(imgCast)
    writer.SetFileDimensionality(3)
    writer.Write()
    
def loadVtkImage(name):
    """
    load a VTK Image (.vtk) into a vtkImageData (vtkStructuredPoints)
    """
    reader = vtk.vtkStructuredPointsReader()
    reader.SetFileName(name)
    reader.Update()    
    return reader.GetOutput()

def saveVtkImage(name, image, asciiorbin='binary', coding='double'):
    """
    save a VTK Image (.vtk) from a vtkImageData (binary)
    ! "uchar image"+ascii => "float image" (cfr. vtkDataWriter)
      "uchar image"+binary => "uchar image"
    """
    name = os.path.splitext(name)[0] + '.vtk'
    imgCast = castImage(image, coding)
    writer = vtk.vtkStructuredPointsWriter();
    if asciiorbin=='binary':
        writer.SetFileTypeToBinary()
    else:
        writer.SetFileTypeToASCII()    
    writer.SetInput(imgCast);
    writer.SetFileName(name)
    writer.Write() # really slow if ASCII!!!
    
def loadVtkImageXML(name):
    """
    load a VTK Image (.vti) into a vtkImageData (vtkStructuredPoints)
    """
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(name)
    reader.Update()    
    return reader.GetOutput()

def saveVtkImageXML(name, image, asciiorbin='binary', coding='uchar'):
    """
    save a VTK Image (.vti) from a vtkImageData (binary)
    """
    name = os.path.splitext(name)[0] + '.vti'
    imgCast = castImage(image, coding)
    writer = vtk.vtkXMLImageDataWriter();
    compressor = vtk.vtkZLibDataCompressor()
    writer.SetCompressor(compressor)
    if asciiorbin=='binary':
        writer.SetDataModeToBinary()
    else:
        writer.SetDataModeToAscii()
    writer.SetInput(imgCast);
    writer.SetFileName(name)
    writer.Write()

def loadGenesisImage(directory, range=(1,60)):
    reader = vtk.vtkGESignaReader()
    reader.SetDataExtent(0,0,0,0,range[0],range[1])
    #reader.SetFileNameSliceOffset(1)
    reader.SetFilePrefix(directory)
    reader.SetFilePattern ("%s/I.%03d")
    #print 'header size =', reader.GetHeaderSize()
    #print 'format =', reader.GetDescriptiveName()
    reader.Update()
    return reader.GetOutput()
    
def loadDicomImage(directory):
    reader = vtk.vtkDICOMImageReader()
    reader.SetDirectoryName(directory)
    reader.Update()
    print "Spacing = ", reader.GetPixelSpacing()[0],reader.GetPixelSpacing()[1],reader.GetPixelSpacing()[2]
    print "NumberOfComponents = ", reader.GetNumberOfComponents()
    print "TransferSyntaxUID =", reader.GetTransferSyntaxUID()
    print "RescaleSlope =", reader.GetRescaleSlope()
    print "RescaleOffset =", reader.GetRescaleOffset()
    print "PatientName =", reader.GetPatientName()
    print "StudyUID =", reader.GetStudyUID()
    print "StudyID =", reader.GetStudyID()
    print "description = ",reader.GetDescriptiveName ()
    print "width = ", reader.GetWidth()
    print "height = ", reader.GetHeight()
    print "patientPosition = ", reader.GetImagePositionPatient ()
    print "patientOrientation = ", reader.GetImageOrientationPatient ()
    print "pixelRepresentation = ", reader.GetPixelRepresentation ()
    print "name = ",reader.GetDescriptiveName ()
    print "ext = ", reader.GetFileExtensions ()
    print "bits allocated = ";reader.GetBitsAllocated ()
    return reader.GetOutput()

def loadTifImage(filename):

    step = 1.0
    
    import os, os.path
    dir = os.path.split(filename)[0]
    name = os.path.split(filename)[1]
    
    for file in os.listdir(dir):
        if os.path.splitext(file)[1] == '.log':
            logfile = file
            break
    
    print 'logfile',dir+'/'+logfile
    
    inFile = open(dir+'/'+logfile, 'r')
    line = inFile.readline().split()
    
    eof = False
    while not eof: 
        if len(line) == 0:
            line = inFile.readline().split()
            if len(line) == 0:
                eof = True
        if (len(line)==4) and line[0] == 'Result' and line[1] == 'Image' and line[2] == 'Width' :
            resultimagewidth = line[3]
        if (len(line)==4) and line[0] == 'Result' and line[1] == 'Image' and line[2] == 'Height' :
            resultimageheight = line[3]
        if (len(line)==3) and line[0] == 'Pixel' and line[1] == 'Size' :
            pixelsize = line[2]
        line = inFile.readline().split()
        
    resultimagewidth = int(resultimagewidth.partition('=')[2])
    resultimageheight = int(resultimageheight.partition('=')[2])
    spacing = float(pixelsize.partition('=')[2])
        
    if pixelsize.partition('=')[0] == '(um)':
        spacing = spacing * 0.001
   
    names = os.listdir(dir)
    nboffiles =  len(names)-2
    nameonly = os.path.splitext(name)[0]
    fileprefix = os.path.join(dir,nameonly.rpartition('_')[0]+'_')  
     
    reader = vtk.vtkTIFFReader()
    reader.SetFileDimensionality(2);
    reader.SetNumberOfScalarComponents(1);
    
    print 'spacing: ',spacing,spacing,spacing*step
    print 'dimensions: ',resultimagewidth, resultimageheight, nboffiles
    print 'extent: ',0,resultimagewidth-1,0,resultimageheight-1,0,nboffiles-1
    print 'bounds: ',0,resultimagewidth*spacing,0,resultimageheight*spacing,0,nboffiles*spacing*step

    reader.SetFilePrefix(fileprefix);
    if len(nameonly.rpartition('_')[2])==2:
        reader.SetFilePattern("%s%02d.tif")
    elif len(nameonly.rpartition('_')[2])==3:
        reader.SetFilePattern("%s%03d.tif")
    reader.SetDataSpacing( 1.0, 1.0, step) # bizarre: si je mets (spacing,spacing,spacing*step) et remplace par (1.0,1.0,spacing*step) -> vtkImageChangeInformation
    reader.SetDataExtent(0,resultimagewidth-1,0,resultimageheight-1,0,nboffiles-1)
    reader.Update()
    
    rescale = vtk.vtkImageChangeInformation()
    rescale.SetInput(reader.GetOutput())
    rescale.SetOutputOrigin(0.0,0.0,0.0)
    rescale.SetSpacingScale(spacing,spacing,spacing)
    rescale.Update()
    
    return rescale.GetOutput()

def loadPolyData(name):
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(name)
    reader.Update()
    return reader.GetOutput()

def savePolyData(name, polydata, asciiorbin='binary'):
    """
    save a polydata to disk in vtk format
    """
    name = os.path.splitext(name)[0] + '.vtk'
    writer = vtk.vtkPolyDataWriter()
    writer.SetFileName(name)
    if asciiorbin=='binary':
        writer.SetFileTypeToBinary()
    else:
        writer.SetFileTypeToASCII()
    writer.SetInput(polydata)
    writer.Write()

def loadPolyDataXML(name):
    """
    load a VTK PolyData (.vtp) into a vtkPolyData using XML format
    """
    name = os.path.splitext(name)[0] + '.vtp'
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(name)
    reader.Update()
    return reader.GetOutput()
    
def loadStl(name):
    """
    load a STL Surface (.stl) into a vtkPolyData
    """
    reader = vtk.vtkSTLReader()
    reader.SetFileName(name)
    reader.Update()    
    return reader.GetOutput()
    
def savePolyDataXML(name, image, asciiorbin='binary'):
    """
    save a VTK PolyData (.vtp) from a vtkPolyData using XML format
    """
    writer = vtk.vtkXMLPolyDataWriter()
    compressor = vtk.vtkZLibDataCompressor()
    writer.SetCompressor(compressor)
    if asciiorbin=='binary':
        writer.SetDataModeToBinary() # marche pas...
    else:
        writer.SetDataModeToAscii()
    writer.SetInput(image);
    writer.SetFileName(name)
    writer.Write()
    
def loadUgrid(name):
    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName(name)
    reader.Update()
    return reader.GetOutput()

def saveUgrid(name, ugrid, asciiorbin='binary'):
    """
    save a ugrid to disk in vtk format
    """
    writer = vtk.vtkUnstructuredGridWriter()
    writer.SetFileName(name)
    if asciiorbin=='binary':
        writer.SetFileTypeToBinary()
    else:
        writer.SetFileTypeToASCII()
    writer.SetInput(ugrid)
    writer.Write()

def loadUgridXML(name):
    """
    load a VTK UntructuredGrid (.vtu) into a vtkUntructuredGrid using XML format
    """
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(name)
    reader.Update()
    return reader.GetOutput()

def saveUgridXML(name, ugrid, asciiorbin='binary'):
    """
    save a VTK UntructuredGrid (.vtu) from a vtkUntructuredGrid using XML format
    """
    writer = vtk.vtkXMLUnstructuredGridWriter()
    compressor = vtk.vtkZLibDataCompressor()
    writer.SetCompressor(compressor)
    if asciiorbin=='binary':
        writer.SetDataModeToBinary() # marche pas...
    else:
        writer.SetDataModeToAscii()
    writer.SetInput(ugrid);
    writer.SetFileName(name)
    writer.Write()
    
def createBoxWidget(image, iren):
    boxWidget = vtk.vtkBoxWidget()
    boxWidget.SetInteractor(iren)
    boxWidget.SetPlaceFactor(1.0)
    boxWidget.SetInput(image)
    boxWidget.PlaceWidget()
    boxWidget.InsideOutOn()
    outlineProperty = boxWidget.GetOutlineProperty()
    outlineProperty.SetRepresentationToWireframe()
    outlineProperty.SetAmbient(1.0)
    outlineProperty.SetAmbientColor(0, 0, 0)
    outlineProperty.SetLineWidth(2)
    selectedOutlineProperty = boxWidget.GetSelectedOutlineProperty()
    selectedOutlineProperty.SetRepresentationToWireframe()
    selectedOutlineProperty.SetAmbient(1.0)
    selectedOutlineProperty.SetAmbientColor(1, 0, 0)
    selectedOutlineProperty.SetLineWidth(3)
    return boxWidget
           
def vtk2gmsh(polydata, filename='out.geo'):
    file = open(filename,'w')
    lc=4 # a parametrer!!

    nbnod = polydata.GetNumberOfPoints()
    nbelm = polydata.GetNumberOfCells()
    print 'writing',nbnod,'nodes and',nbelm,'elements'

    file.write("lc=%d;\n" % lc)

    for i in range(0,nbnod):
        line=polydata.GetPoints().GetPoint(i)
        file.write("Point(%d)={%e,%e,%e,lc};\n" % (i+1, float(line[0]), float(line[1]), float(line[2])))

    edges={}
    nextno=1
    for i in range(0,nbelm):
        cell=polydata.GetCell(i)
        line=cell.GetPointIds()
        if cell.GetNumberOfPoints()!=3:
            print "bad elem (%d nodes)" % cell.GetNumberOfPoints()
            file.close()
            sys.exit()
        n1=cell.GetPointId(0)+1
        n2=cell.GetPointId(1)+1
        n3=cell.GetPointId(2)+1
        eds = [(n1,n2),(n2,n3),(n3,n1)]
        edno = [0, 0, 0]
        for j in range(0,3):
            edge=eds[j];
            sign=1
            edno[j]=0
            if edge[0]>edge[1]:
                sign=-1
                edge=(edge[1],edge[0])
            if edges.has_key(edge):
                edno[j]=edges[edge]*sign
            else:
                edno[j]=nextno*sign
                edges[edge]=nextno
                file.write("Line(%d) = {%d,%d};\n" %(nextno, edge[0], edge[1]))
                nextno=nextno+1
        file.write("Line Loop(%d) = {%d,%d,%d};\n" % (nextno, edno[0], edno[1], edno[2]))
        file.write("Plane Surface(%d) = {%d};\n" % (i+1, nextno))
        nextno=nextno+1

    file.write("Coherence;\n")
    file.write("Surface Loop(%d) = {" % (nbelm+1))
    for i in range(0,nbelm):
        file.write("%d" % (i+1))
        if i==nbelm-1:
            file.write("};\n")
        else:
            file.write(",")
    file.write("Volume(1) = {%d};\n" % (nbelm+1))
    file.write("Physical Volume(1) = {1};\n")
    file.write("Mesh.CharacteristicLengthFactor = %d;\n" % lc)
    file.close()

def loadPolyFile(name = "surfmesh.poly"):
    """
    read .poly file  - tetgen input file
    """
    polydata = vtk.vtkPolyData()
    points   = vtk.vtkPoints()
    polys    = vtk.vtkCellArray()
    
    inFile = open(name, 'r')
    
    line=inFile.readline().split()
    nbnod = 0
    while 1:
        try: 
            nbnod = int(line[0])
            break
        except:
            line=inFile.readline().split()
  
    for i in range(0,nbnod):
        line=inFile.readline().split()
        points.InsertPoint(i, float(line[1]), float(line[2]), float(line[3]))
    
    nbelm = 0
    line=inFile.readline().split()
    while 1:
        try: 
            nbelm = int(line[0])
            break
        except:
            line=inFile.readline().split()

    for i in range(0,nbelm):
        line=inFile.readline().split()
        if int(line[0])!=3:
            print "bad elem (%d nodes)" % int(line[0])
            sys.exit()
        n1=int(line[1])
        n2=int(line[2])
        n3=int(line[3])
        polys.InsertNextCell(3)
        polys.InsertCellPoint(n1-1)
        polys.InsertCellPoint(n2-1)
        polys.InsertCellPoint(n3-1)    
            
    polydata.SetPoints(points)
    polydata.SetPolys(polys)
    print polydata
    return polydata    
    
def loadPwnFile1(filename): #.pwn file: pt0 pt1 pt2 n0 n1 n2
    print "loadPwnFile"
    inFile = open(filename, 'r')
    line = inFile.readline().split()  
    nbnod = int(line[0])  
    points = vtk.vtkPoints()
    vectors = vtk.vtkFloatArray()
    vectors.SetName("normals")
    vectors.SetNumberOfComponents(3)
    for i in range(0,nbnod):
        line=inFile.readline().split()
        points.InsertPoint(i, float(line[0]), float(line[1]), float(line[2]))
        vectors.InsertTuple3(i, float(line[3]), float(line[4]), float(line[5]))
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points);
    polydata.GetPointData().SetVectors(vectors)
    print polydata.GetPointData().GetVectors("normals")
    return polydata

def loadPwnFile2(filename): #.pwn file pt0 pt1 pt2 ..... ( all points)  ... n0 n1 n2 (all normals)
    print "loadPwnFile2"
    inFile = open(filename, 'r')
    line = inFile.readline().split()  
    nbnod = int(line[0])  
    
    points = vtk.vtkPoints()
    for i in range(0,nbnod):
        line=inFile.readline().split()
        points.InsertPoint(i, float(line[0]), float(line[1]), float(line[2]))
    
    vectors = vtk.vtkFloatArray()
    vectors.SetName("normals")
    vectors.SetNumberOfComponents(3)
    for i in range(0,nbnod):
        line=inFile.readline().split()
        vectors.InsertTuple3(i, float(line[0]), float(line[1]), float(line[2]))
            
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points);
    polydata.GetPointData().SetVectors(vectors)
    print polydata.GetPointData().GetVectors("normals")
    
    return polydata

def loadPtsFile(filename): #.pts file
    inFile = open(filename, 'r')
    line = inFile.readline().split()  
    nbnod = int(line[0])  
    points = vtk.vtkPoints()
    for i in range(nbnod):
        line=inFile.readline().split()
        points.InsertNextPoint(float(line[0]), float(line[1]), float(line[2]))
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points);
    print polydata.GetNumberOfPoints ()
    return polydata
    
def tetgen2vtk(name="mesh", arrayName = "doubledNode"):
    """
    read tetgen output files into memory (ugrid)
    """
    ugrid  = vtk.vtkUnstructuredGrid()
    points = vtk.vtkPoints()
    inFile = open(name+".1.node", 'r')
    line = inFile.readline().split()
    nbnod = int(line[0])
    vtkArray = vtk.vtkIntArray()
    if arrayName:
        vtkArray.SetName(arrayName)
    vtkArray.SetNumberOfValues(nbnod);
    for i in range(nbnod):
        line=inFile.readline().split()
        points.InsertPoint(i, float(line[1]), float(line[2]), float(line[3]))
        try:
            vtkArray.SetValue(i,int(line[4])-1) #car on renumerote a nouveau a partir de 1
        except:
            vtkArray.SetValue(i,-1)
            
    ugrid.GetPointData().AddArray(vtkArray)
    inFile.close()
    ugrid.SetPoints(points)

    inFile = open(name+".1.ele", 'r')
    line = inFile.readline().split()
    nbelm = int(line[0])
    materArray = vtk.vtkIntArray()
    materArray.SetName("material label")
    materArray.SetNumberOfValues(nbelm)
    for i in range(0,nbelm):
        line=inFile.readline().split()
        n1=int(line[1])-1
        n2=int(line[2])-1
        n3=int(line[3])-1
        n4=int(line[4])-1
        tetra = vtk.vtkTetra()
        tetra.GetPointIds().SetId(0, n1)
        tetra.GetPointIds().SetId(1, n2)
        tetra.GetPointIds().SetId(2, n3)
        tetra.GetPointIds().SetId(3, n4)
        ugrid.InsertNextCell(tetra.GetCellType(),
                             tetra.GetPointIds())
        try:
            materArray.SetValue(i,int(line[5]))
        except: # no material label
            materArray.SetValue(i,1)
            
    ugrid.GetCellData().AddArray(materArray)
    inFile.close()
    
    return ugrid

def tetgen2vtkGetMarkedBoundaryNodes(marker = 1, name="surfmesh"):
    """
    read tetgen output files into memory (ugrid)
    """
    markedBoundaryNodes = []
    inFile = open(name+".1.node", 'r')
    line = inFile.readline().split()
    nbnod = int(line[0])
    for i in range(1,nbnod+1):
        line=inFile.readline().split()
        if (int(line[4]) == int(marker)):
            markedBoundaryNodes.append(i)
    inFile.close()
    
    return markedBoundaryNodes

def off2vtk(name="ellipse.off"):
    """
    read an OOGL (isosurf output) file into memory (polydata)
    """
    inFile = open(name, 'r')
    tag = inFile.readline()
    if tag[0:4]!="NOFF":
        print "bad format!"
        sys.exit()
    line = inFile.readline().split()
    nbnod = int(line[0])
    nbelm = int(line[1])
    #print 'reading',nbnod,'nodes and',nbelm,'elements'

    polydata = vtk.vtkPolyData()
    points   = vtk.vtkPoints()
    polys    = vtk.vtkCellArray()

    for i in range(0,nbnod):
        line=inFile.readline().split()
        points.InsertPoint(i, float(line[0]), float(line[1]), float(line[2]))

    for i in range(0,nbelm):
        line=inFile.readline().split()
        if int(line[0])!=3:
            print "bad elem (%d nodes)" % int(line[0])
            sys.exit()
        n1=int(line[1])
        n2=int(line[2])
        n3=int(line[3])
        #polys.InsertNextCell(3, [n1, n2, n3]) # marche pas sous python
        polys.InsertNextCell(3)
        polys.InsertCellPoint(n1)
        polys.InsertCellPoint(n2)
        polys.InsertCellPoint(n3)

    polydata.SetPoints(points)
    polydata.SetPolys(polys)
    return polydata  
        
def printVtkImageInfo(image, title = ' vtkImageData info '):
    print '-- ',title,' --'
    print 'spacing: ',image.GetSpacing()
    print 'dimensions: ',image.GetDimensions()
    print 'origin: ',image.GetOrigin()
    print 'extent: ',image.GetExtent()
    
def readImageScalarRange(filename, extent=(0,255,0,255,0,59), coding='ushort'):
    """
    display scalar range of a file (no vtk call - python only)
    """
    import struct
    l=(extent[1]-extent[0]+1)*(extent[3]-extent[2]+1)*(extent[5]-extent[4]+1)
    typeDataIn=str(l)
    if coding=='ushort':
        typeDataIn=typeDataIn+'H' # unsigned short
    elif coding=='uchar':
        typeDataIn=typeDataIn+'B' # unsigned char
    else:
        print 'bad coding : %s' % coding
        sys.exit(1)
    # read file
    file = open(filename, 'rb')
    allfile = file.read()
    file.close()

    value = struct.unpack(typeDataIn, allfile[0:struct.calcsize(typeDataIn)])
    range = (min(value), max(value))
    return range
    
def printOneLineOfData(filename, slice=30, line=128, extent=(0,255,0,255,0,59), coding='ushort'):  
    import struct

    typeDataIn=''
    if coding=='ushort':
        typeDataIn=typeDataIn+'H' # unsigned short
    elif coding=='uchar':
        typeDataIn=typeDataIn+'B' # unsigned char
    else:
        print 'bad coding : %s' % coding
        sys.exit(1)

    # read file
    file = open(filename, 'rb')
    allfile = file.read()
    file.close()

    # display a line on the screen
    sizIn = struct.calcsize(typeDataIn)
    
    lx=extent[1]-extent[0]+1
    ly=extent[3]-extent[2]+1
    lz=extent[5]-extent[4]+1
    
    start=sizIn*(lx*ly*slice+lx*line)
    for j in range(extent[0],extent[1]):
        value = struct.unpack(typeDataIn, allfile[start:start+sizIn])[0]
        print value,
        start=start+sizIn
    print ''
