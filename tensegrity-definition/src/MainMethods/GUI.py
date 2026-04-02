import json
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from typing import List

from src.PayloadOptimizer.SimplifiedTensegrityModel import SimplifiedTensegrityModel
from src.PayloadOptimizer.PayloadOptimizer import PayloadOptimizer
from src.PayloadOptimizer.GA import geneticAlg
from src.TensegritySystem import Systems, ClassK_Test as ckt, Nodes, TensegrityClassKConvert as tkc
from src.Utils import CommonMatrixOperations, SaveData, PreloadedConfigurations, TensegrityPlotter as plot


class GUI:
    def __init__(self):

        # These are the preconfigured options, so they don't have to be typed in every time.
        self.options: List[str] = ['doublePendulumConfig', 'icosahedronConfig', 'tensegrityJointConfig']
        self.root: tk.Tk = tk.Tk()
        self.root.title("Tensegrity Calculations")

        # The following variables are global variables that are accessible all over the gui, and are changed using the same methods.
        self.clicked: tk.StringVar = tk.StringVar()
        self.numOfBars: tk.IntVar = tk.IntVar()
        self.numOfNode: tk.IntVar = tk.IntVar()
        self.numOfPinnedNode: tk.IntVar = tk.IntVar()
        self.numOfStrings: tk.IntVar = tk.IntVar()
        self.prestress: tk.DoubleVar = tk.DoubleVar()
        self.pinnedNodes: np.ndarray[np.ndarray[int]] = np.zeros(self.numOfPinnedNode.get())

        # The following are variables that are based off the original input.
        self.barConnectivityMatrix: np.ndarray[np.ndarray[float]] = np.zeros([self.numOfBars.get(), 2])
        self.coordinateNodeArray: np.ndarray[np.ndarray[float]] = np.zeros([self.numOfNode.get(), 3])
        self.forcesOnNodesArray: np.ndarray[np.ndarray[float]] = np.zeros([self.numOfNode.get(), 3])
        self.initialRotation: float = 0
        self.initialVelocities: np.ndarray[np.ndarray[float]] = np.zeros([self.numOfNode.get(), 3])
        self.stringConnectivityMatrix: np.ndarray[np.ndarray[float]] = np.zeros([self.numOfStrings.get(), 2])

        # The following variables are Entries that other functions need to see outside the main loop.
        self.axisValueEntry: tk.Entry = tk.Entry(master=self.root, fg='black', bg='lightgray', width=20, justify="left")
        self.dampingValueEntry: tk.Entry = tk.Entry(master=self.root, fg='black', bg='lightgray', width=40)
        self.dtValueEntry: tk.Entry = tk.Entry(master=self.root, fg='black', bg='lightgray', width=40)
        self.fileNameEntry: tk.Entry = tk.Entry(master=self.root, fg='black', bg='lightgray', width=20, justify="left")
        self.numOfBarsEntry: tk.Entry = tk.Entry(master=self.root, fg='black', bg='lightgray', width=40, textvariable=self.numOfBars)
        self.numOfNodesEntry: tk.Entry = tk.Entry(master=self.root, fg='black', bg='lightgray', width=40, textvariable=self.numOfNode)
        self.numOfPinnedEntry: tk.Entry = tk.Entry(master=self.root, fg='black', bg='lightgray', width=40, textvariable=self.numOfPinnedNode)
        self.numOfStringsEntry: tk.Entry = tk.Entry(master=self.root, fg='black', bg='lightgray', width=40, textvariable=self.numOfStrings)
        self.prestressEntry: tk.Entry = tk.Entry(master=self.root, fg='black', bg='lightgray', width=40, textvariable=self.prestress)
        self.tfValueEntry: tk.Entry = tk.Entry(master=self.root, fg='black', bg='lightgray', width=40)

        # The check buttons and booleans needed in other areas of the code.
        self.haveVideo: tk.BooleanVar = tk.BooleanVar()
        self.makeFile: tk.BooleanVar = tk.BooleanVar()
        self.seePlot: tk.BooleanVar = tk.BooleanVar()
        self.updateForces: tk.BooleanVar = tk.BooleanVar()
        self.useGround: tk.BooleanVar() = tk.BooleanVar()
        self.useController: tk.BooleanVar() = tk.BooleanVar()

        self.nonConstForceCheckButton: tk.Checkbutton = tk.Checkbutton(self.root, text='NonConstant Forces', variable=self.updateForces,
                                                                       onvalue=True, offvalue=False)
        self.useControllerCheckButton: tk.Checkbutton = tk.Checkbutton(self.root, text='Use Controller', variable=self.useController,
                                                                       onvalue=True, offvalue=False)
        self.useGroundCheckButton: tk.Checkbutton = tk.Checkbutton(self.root, text='Use Ground', variable=self.useGround,
                                                                   onvalue=True, offvalue=False)

        self.createVideoCheckButton: tk.Checkbutton = tk.Checkbutton(self.root, text='Check to create a video.', variable=self.haveVideo,
                                                                     onvalue=True, offvalue=False, justify="left")
        self.showPlotCheckButton: tk.Checkbutton = tk.Checkbutton(self.root, text='Check for initial system plot.', variable=self.seePlot,
                                                                  onvalue=True, offvalue=False, justify="left")
        self.saveHistoryToFileCheckButton: tk.Checkbutton = tk.Checkbutton(self.root, text='Check to save history to file.', variable=self.makeFile,
                                                                           onvalue=True, offvalue=False, justify="left")

    class GUIParams:
        def __init__(self, axisLength: float, barConnMat: np.ndarray[np.ndarray[int]], coordinateNodeArray: np.ndarray[np.ndarray[float]], createVideo: bool,
                     damping: float, dt: float, filename: str,
                     forces: np.ndarray[np.ndarray[int]],
                     initialRotation: float, nonconstForces: bool, numOfBars: int, numOfNode: int, numOfPinned: int, numOfStrings: int, initialVelocities:
                np.ndarray[np.ndarray[float]],
                     pinnedNodes, prestress: float, saveHistory: bool, showPlot: bool, stringConnectivityMatrix: np.ndarray[np.ndarray[int]], tf: float,
                     Use_Controller: bool,
                     Use_Ground: bool):
            self.axisLength = axisLength
            self.barConnectivityMatrix = barConnMat.tolist()
            self.coordinateNodeArray = coordinateNodeArray.tolist()
            self.createVideo = createVideo
            self.damping = damping
            self.dt = dt
            self.filename = filename
            self.forcesOnNodesArray = forces.tolist()
            self.initialRotation = initialRotation
            self.nonConstantForces = nonconstForces
            self.numOfBars = numOfBars
            self.numOfNode = numOfNode
            self.numOfPinned = numOfPinned
            self.numOfStrings = numOfStrings
            self.initialVelocities = initialVelocities.tolist()
            self.prestress = prestress
            self.saveHistory = saveHistory
            self.showPlot = showPlot
            self.stringConnectivityMatrix = stringConnectivityMatrix.tolist()
            self.tf = tf
            self.useController = Use_Controller
            self.useGround = Use_Ground

            if type(pinnedNodes) != list:
                self.pinnedNodes = pinnedNodes.tolist()
            else:
                self.pinnedNodes = pinnedNodes

        def toJSON(self, fileName: str):

            data = json.dumps(self, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)
            print(data)
            with open(f'placeholderFolders/jsonConfigs/{fileName}.json', 'w') as f:
                f.write(data)

    class SurrogateOptimizer:
        def __init__(self, nodeMass: float, springConstant: float, filename: str):
            """"""
            self.tensModel: SimplifiedTensegrityModel = SimplifiedTensegrityModel(nodeMass, springConstant, timeFinal=1)

            initialPosition: np.ndarray[np.ndarray[float]] = self.tensModel.getInitialState()
            initialVelocity: np.ndarray[np.ndarray[float]] = np.zeros([7, 3])
            self.initialState: np.ndarray[np.ndarray[float]] = np.append(initialPosition, initialVelocity, axis=0)

            self.initialState.T[2][10:13] = np.ones(3) * 31.3

            self.tensModel.setInitialFullState(self.initialState)

            self.filename = filename
            self.results: np.ndarray[np.ndarray[float]] = None

            self.optimizer: PayloadOptimizer = PayloadOptimizer(self.tensModel)

            self.result: np.ndarray[float] = np.array([0, 0, 0, 0])

        def plotModel(self):
            """"""
            self.tensModel.plotFigure()

        def optimize(self):
            """"""
            self.results = self.optimizer.optimize()

        def setTensModelConstants(self, equSpringConst: float, stiffSpringConst: float, structureSize: float, payloadLocation: float):
            """"""
            self.tensModel.setEquSpringConst(equSpringConst)
            self.tensModel.setStiffSpringConstant(stiffSpringConst)
            self.tensModel.setStructureSize(structureSize)
            self.tensModel.setPayloadLocation(payloadLocation)

        def showModelMotion(self, initialState: List[float]):
            """"""
            self.tensModel.rk4(initialState)
            self.tensModel.animateMotion(self.filename)

    def convertNeededVarsToInts(self) -> None:
        """
        Changes float values into integers inside arrays that require int values.
        :return: None
        """
        for i in range(len(self.barConnectivityMatrix)):
            for j in range(len(self.barConnectivityMatrix[i])):
                self.barConnectivityMatrix[i][j] = int(self.barConnectivityMatrix[i][j])

        for i in range(len(self.stringConnectivityMatrix)):
            for j in range(len(self.stringConnectivityMatrix[i])):
                self.stringConnectivityMatrix[i][j] = int(self.stringConnectivityMatrix[i][j])

        for i in range(len(self.pinnedNodes)):
            self.pinnedNodes[i] = int(self.pinnedNodes[i])

    def editPairedVars(self, varToChange: np.ndarray[np.ndarray[float]], window: tk.Tk, windowTitle: str) -> None:
        """
        Creates a popup window in tkInter with a variable to change given.
        :param varToChange: the variable that is created in the popup that will be edited by the user.
        :param window: the main root window
        :param windowTitle: The title of the window.
        :return:
        """
        top = tk.Toplevel(window)
        top.geometry("750x750")

        if 0 < varToChange.size:
            tk.Label(top, text=windowTitle, font='Mistral 18 bold').grid(row=0, column=0, columnspan=len(varToChange[0]))
            eGrid: List[List[tk.Entry]] = [[]]
            for i in range(len(varToChange) + 2):
                eRow: List[tk.Entry] = []
                for j in range(len(varToChange[0]) + 1):
                    if 0 == i:
                        pass
                    else:
                        e = tk.Entry(top, width=10, fg='blue', font=('Arial', 16, 'bold'))
                        e.grid(row=i, column=j)
                        eRow.append(e)

                        if 1 == i:
                            if 0 == j:
                                e.insert(tk.END, "")
                            elif 1 == j:
                                e.insert(tk.END, "1st Node")
                            else:
                                e.insert(tk.END, "2nd Node")
                        elif 0 == j:
                            e.insert(tk.END, str(i - 1))
                        else:
                            e.insert(tk.END, str(varToChange[i - 2][j - 1]))

                if 0 < len(eRow):
                    if 0 < np.array(eGrid).size:
                        eGrid.append(eRow)
                    else:
                        eGrid = [eRow]

            b = tk.Button(top, text="SAVE", command=lambda: self.saveInfoAndClosePopup(top, varToChange, eGrid))
            b.grid(row=len(varToChange) + 1, column=0, columnspan=len(varToChange[0]))
        else:
            tk.Label(top, text=windowTitle, font='Mistral 18 bold').grid(row=0, column=0)
            tk.Label(top, text="No Entries to edit.").grid(row=1, column=0)
            b = tk.Button(top, text="SAVE", command=top.destroy)

        b.grid(row=len(varToChange) + 5, column=0)

    def editPinnedVars(self, varToChange: np.ndarray[float], window: tk.Tk, windowTitle: str) -> None:
        """
        changes the PinnedNodes variable through GUI interaction.
        :param varToChange: The variable that is changed.
        :param window: The GUI window
        :param windowTitle: The Title for the window.
        :return: None
        """
        top = tk.Toplevel(window)
        top.geometry("750x750")

        if 0 < len(varToChange):
            tk.Label(top, text=windowTitle, font='Mistral 18 bold').grid(row=0, column=0, columnspan=len(varToChange))
            eGrid: List[tk.Entry] = []
            for i in range(len(varToChange)):
                e = tk.Entry(top, width=10, fg='blue', font=('Arial', 16, 'bold'))
                e.grid(row=i + 1, column=0)
                eGrid.append(e)
                e.insert(tk.END, str(varToChange[i]))

            b = tk.Button(top, text="SAVE", command=lambda: self.saveInfoAndClosePopupPinned(top, varToChange, eGrid))
        else:
            tk.Label(top, text=windowTitle, font='Mistral 18 bold').grid(row=0, column=0)
            tk.Label(top, text="No Entries to edit.").grid(row=1, column=0)
            b = tk.Button(top, text="SAVE", command=top.destroy)

        b.grid(row=len(varToChange) + 5, column=0)

    def editVarsWithXYZ(self, varToChange: np.ndarray[np.ndarray[float]], window: tk.Tk, windowTitle: str) -> None:
        """
        Creates a popup window in tkInter with a variable to change given.
        :param varToChange: the variable that is created in the popup that will be edited by the user.
        :param window: the main root window
        :param windowTitle: The title of the window.
        :return:
        """
        top = tk.Toplevel(window)
        top.geometry("750x750")
        if 0 < varToChange.size:
            tk.Label(top, text=windowTitle, font='Mistral 18 bold').grid(row=0, column=0, columnspan=len(varToChange[0]))
            eGrid: List[List[tk.Entry]] = [[]]
            for i in range(len(varToChange) + 2):
                eRow: List[tk.Entry] = []
                for j in range(len(varToChange[0]) + 1):
                    if 0 == i:
                        pass
                    else:
                        e = tk.Entry(top, width=10, fg='blue', font=('Arial', 16, 'bold'))
                        e.grid(row=i, column=j)
                        eRow.append(e)

                        if 1 == i:
                            if 0 == j:
                                e.insert(tk.END, "")
                            else:
                                e.insert(tk.END, chr(ord('w') + j))
                        elif 0 == j:
                            e.insert(tk.END, str(i - 1))
                        else:
                            e.insert(tk.END, str(varToChange[i - 2][j - 1]))

                if 0 < len(eRow):
                    if 0 < np.array(eGrid).size:
                        eGrid.append(eRow)
                    else:
                        eGrid = [eRow]

            b = tk.Button(top, text="SAVE", command=lambda: self.saveInfoAndClosePopup(top, varToChange, eGrid))
        else:
            tk.Label(top, text=windowTitle, font='Mistral 18 bold').grid(row=0, column=0)
            tk.Label(top, text="No Entries to edit.").grid(row=1, column=0)
            b = tk.Button(top, text="SAVE", command=top.destroy)

        b.grid(row=len(varToChange) + 5, column=0, columnspan=len(varToChange[0]))

    def exportCurrentStateToFile(self) -> None:
        """
        This function takes the current state of the system and exports it to a file, so that it can be imported in the future.
        :return: None
        """
        classToExport = self.GUIParams(float(self.axisValueEntry.get()), self.barConnectivityMatrix, self.coordinateNodeArray, self.haveVideo.get(),
                                       float(self.dampingValueEntry.get()), float(self.dtValueEntry.get()), self.fileNameEntry.get(), self.forcesOnNodesArray,
                                       self.initialRotation, self.updateForces.get(), int(self.numOfBars.get()), int(self.numOfNode.get()),
                                       int(self.numOfPinnedNode.get()),
                                       int(self.numOfStrings.get()), self.initialVelocities, self.pinnedNodes, float(self.prestress.get()), self.makeFile.get(),
                                       self.seePlot.get(), self.stringConnectivityMatrix, float(self.tfValueEntry.get()), self.useController.get(),
                                       self.useGround.get())

        classToExport.toJSON(self.fileNameEntry.get())

    def importStateFromFile(self) -> None:
        """
        This function imports a configuration from a file.
        :return: None
        """
        filename: str = askopenfilename(initialdir="placeholderFolders/jsonConfigs")
        data: dict = json.load(open(filename, 'r'))
        self.loadConf(data)
        self.barConnectivityMatrix = np.array(self.barConnectivityMatrix)
        self.stringConnectivityMatrix = np.array(self.stringConnectivityMatrix)
        self.coordinateNodeArray = np.array(self.coordinateNodeArray)
        self.initialVelocities = np.array(self.initialVelocities)
        self.forcesOnNodesArray = np.array(self.forcesOnNodesArray)

    def loadConf(self, dictToLoad=None) -> None:
        """
        Loads configuration parameters into the GUI so that manual manipulation is not needed.
        :return: None
        """
        if dictToLoad is None:
            dictToLoad: dict = dict({})

            if self.clicked.get() == 'doublePendulumConfig':
                dictToLoad = PreloadedConfigurations.doublePendulumConfig
            elif self.clicked.get() == 'icosahedronConfig':
                dictToLoad = PreloadedConfigurations.icosahedronConfig
            elif self.clicked.get() == 'tensegrityJointConfig':
                dictToLoad = PreloadedConfigurations.tensegrityJointConfig

        self.axisValueEntry.delete(0, tk.END)
        self.axisValueEntry.insert(0, str(dictToLoad.get('axisLength')))

        self.dampingValueEntry.delete(0, tk.END)
        self.dampingValueEntry.insert(0, str(dictToLoad.get('damping')))

        self.dtValueEntry.delete(0, tk.END)
        self.dtValueEntry.insert(0, str(dictToLoad.get('dt')))

        self.fileNameEntry.delete(0, tk.END)
        self.fileNameEntry.insert(0, str(dictToLoad.get('filename')))

        self.numOfBarsEntry.delete(0, tk.END)
        self.numOfBarsEntry.insert(0, str(dictToLoad.get('numOfBars')))

        self.numOfNodesEntry.delete(0, tk.END)
        self.numOfNodesEntry.insert(0, str(dictToLoad.get('numOfNode')))

        self.numOfPinnedEntry.delete(0, tk.END)
        self.numOfPinnedEntry.insert(0, str(dictToLoad.get('numOfPinned')))

        self.numOfStringsEntry.delete(0, tk.END)
        self.numOfStringsEntry.insert(0, str(dictToLoad.get('numOfStrings')))

        self.prestressEntry.delete(0, tk.END)
        self.prestressEntry.insert(0, str(dictToLoad.get('prestress')))

        self.tfValueEntry.delete(0, tk.END)
        self.tfValueEntry.insert(0, str(dictToLoad.get('tf')))

        self.barConnectivityMatrix = dictToLoad.get('barConnectivityMatrix')
        self.coordinateNodeArray = dictToLoad.get('coordinateNodeArray')
        self.forcesOnNodesArray = dictToLoad.get('forcesOnNodesArray')
        self.initialRotation = dictToLoad.get('initialRotation')
        self.initialVelocities = dictToLoad.get('initialVelocities')
        self.pinnedNodes = dictToLoad.get('pinnedNodes')
        self.stringConnectivityMatrix = dictToLoad.get('stringConnectivityMatrix')

        if dictToLoad.get('createVideo'):
            self.createVideoCheckButton.select()
        else:
            self.createVideoCheckButton.deselect()

        if dictToLoad.get('saveHistory'):
            self.saveHistoryToFileCheckButton.select()
        else:
            self.saveHistoryToFileCheckButton.deselect()

        if dictToLoad.get('showPlot'):
            self.showPlotCheckButton.select()
        else:
            self.showPlotCheckButton.deselect()

        if dictToLoad.get('nonConstantForces'):
            self.nonConstForceCheckButton.select()
        else:
            self.nonConstForceCheckButton.deselect()

        if dictToLoad.get('useController'):
            self.useControllerCheckButton.select()
        else:
            self.useControllerCheckButton.deselect()

        if dictToLoad.get('useGround'):
            self.useGroundCheckButton.select()
        else:
            self.useGroundCheckButton.deselect()

    @staticmethod
    def makeNodeArray(vals: np.ndarray[np.ndarray[float]]) -> np.ndarray[Nodes.Node]:
        """
        Makes a node array from the vals passed in
        :param vals: the values that contains each of the nodes.
        :return: The created node array.
        """
        nodeArray: np.ndarray[Nodes.Node] = np.array([])
        for i in range(0, len(vals)):
            newNode = Nodes.Node(vals.item(i, 0), vals.item(i, 1), vals.item(i, 2))
            nodeArray = np.append(nodeArray, newNode)

        return nodeArray

    def openSurrogateModelPopup(self) -> None:
        """
        Creates the surrogate model window on the GUI, runs the optimizer and can animate the motion.
        :return: None
        """
        top = tk.Toplevel(self.root)
        top.geometry("1000x750")
        tk.Label(top, height=3, width=40, text="Node Mass:").grid(row=0, column=0)
        nodeMass: tk.Entry = tk.Entry(master=top, fg='black', bg='lightgray', width=20, justify="left")
        nodeMass.insert(0, '1')
        nodeMass.grid(row=1, column=0)

        tk.Label(top, height=3, width=40, text="initialSpringConstant:").grid(row=0, column=1)
        firstSpringConstant: tk.Entry = tk.Entry(master=top, fg='black', bg='lightgray', width=20, justify="left")
        firstSpringConstant.insert(0, '300')
        firstSpringConstant.grid(row=1, column=1)

        tk.Label(top, height=3, width=40, text="fileName:").grid(row=0, column=2)
        fileName: tk.Entry = tk.Entry(master=top, fg='black', bg='lightgray', width=20, justify="left")
        fileName.insert(0, 'optimizer')
        fileName.grid(row=1, column=2)

        tk.Label(top, height=3, width=40, text="pop size:").grid(row=2, column=0)
        popSize: tk.Entry = tk.Entry(master=top, fg='black', bg='lightgray', width=20, justify="left")
        popSize.insert(0, '10')
        popSize.grid(row=3, column=0)

        tk.Label(top, height=3, width=40, text="max generations:").grid(row=2, column=1)
        maxGens: tk.Entry = tk.Entry(master=top, fg='black', bg='lightgray', width=20, justify="left")
        maxGens.insert(0, '5')
        maxGens.grid(row=3, column=1)

        tk.Label(top, height=3, width=40, text="Genetic Algorithm Solution:").grid(row=4, column=1)
        solution: tk.Entry = tk.Entry(master=top, fg='black', bg='lightgray', width=100, justify="left")
        solution.grid(row=5, column=0, columnspan=3)

        ranges = [[1000, 100], [1e-7, 1e-9], [3, .1], [.5, .5]]
        functionSize = 4

        optimizerModel = self.SurrogateOptimizer(float(nodeMass.get()), float(firstSpringConstant.get()), filename=fileName.get())

        tk.Button(top, text="Run Genetic Alg",
                  command=lambda: runAlg(optimizerModel.tensModel.GAValue, populationSize=int(popSize.get()),
                                         numOfFunctions=functionSize, maxGenerations=int(maxGens.get()),
                                         functionRanges=ranges)).grid(row=6, column=1)

        optimizerModel.tensModel.setEquSpringConst(optimizerModel.result.item(0))
        optimizerModel.tensModel.setStiffSpringConstant(optimizerModel.result.item(1))
        optimizerModel.tensModel.setStructureSize(optimizerModel.result.item(2))
        optimizerModel.tensModel.setPayloadLocation(optimizerModel.result.item(3))
        #
        # initialState.T[2][10:13] = np.ones(3) * 40
        # tensModel.setInitialFullState(initialState)

        tk.Button(top, text="Animate Solution",
                  command=lambda: self.surrogateAnimateMotion(optimizerModel, optimizerModel.initialState, fileName.get())).grid(row=7, column=1)

        def runAlg(GAValue, populationSize: int, numOfFunctions: int, maxGenerations: int, functionRanges) -> None:
            """
            This method makes it so a button can set a variable and a field.
            :param GAValue: The Objective function
            :param populationSize: The pop size for the genetic algorithm.
            :param numOfFunctions: The number of functions for the algorithm to attempt to optimize.
            :param maxGenerations: The number of generations to optimize over.
            :param functionRanges: The ranges of the functions to optimize.
            :return: None
            """
            optimizerModel.result = geneticAlg(GAValue, populationSize, functionSize=numOfFunctions, maxGens=maxGenerations, ranges=functionRanges)[0]
            solution.delete(0, tk.END)
            solution.insert(0, str(optimizerModel.result))

    def publishAsTextFile(self, classKTest) -> None:
        """
        Creates a text file of the node history, if specified.
        :param classKTest: An object containing the node history data.
        :return:
        """
        with open('statesFolder\\' + str(self.fileNameEntry.get()) + '.txt', 'a') as f:
            outputStates: np.ndarray[np.ndarray[float]] = classKTest.getNodeHist()
            for i in range(len(outputStates)):
                f.write(str(outputStates[i]))
                f.write('\n')

    def rotateInitialNodes(self, nodeArray: np.ndarray[Nodes.Node]) -> np.ndarray[Nodes.Node]:
        """
        Rotates the initial nodes from a configuration.
        :param nodeArray: the array to be rotated
        :return:  The rotated node array.
        """
        allCoords: np.ndarray[np.ndarray[float]] = np.array([[], [], []])
        nextNodeArray: List[Nodes.Node] = []
        for i in range(len(nodeArray)):
            allCoords = np.append(allCoords, np.array([nodeArray.item(i).getCoords()]).T, axis=1)
            rotatedCoords: np.ndarray[np.ndarray[float]] = CommonMatrixOperations.rotX(nodeArray.item(i).getCoords(), self.initialRotation)

            newNode: Nodes.Node = Nodes.Node(rotatedCoords.item(0), rotatedCoords.item(1), rotatedCoords.item(2))
            nextNodeArray.append(newNode)

        return np.array(nextNodeArray)

    def runSimulation(self) -> None:
        """
        Runs the GUI simulation.
        :return: None
        """
        # This is the response to the second entry box
        nodeArray: np.ndarray[Nodes.Node]
        nodeArray = self.makeNodeArray(self.coordinateNodeArray)
        nodeArray = self.rotateInitialNodes(nodeArray)

        self.convertNeededVarsToInts()
        system: Systems.System = Systems.System(barConn=self.barConnectivityMatrix, nodeArray=nodeArray, stringConn=self.stringConnectivityMatrix)
        system.setPinned(self.pinnedNodes)

        nNew: np.ndarray[np.ndarray[float]]
        cbNew: np.ndarray[np.ndarray[float]]
        csNew: np.ndarray[np.ndarray[float]]
        P: np.ndarray[np.ndarray[float]]
        D: np.ndarray[np.ndarray[float]]
        nodeConstraints: List[List[int]]
        kConvert: tkc.tensegrityKConvert = tkc.tensegrityKConvert(nodeArray, system.getBarConnMat(), system.getStringConnMat(), self.pinnedNodes)
        nNew, cbNew, csNew, P, D, nodeConstraints = kConvert.returnNeededValues()

        print("converted Class K # of nodes: " + str(len(nNew[0])))
        print("Class k node constraints:")
        for i in range(0, len(nodeConstraints)):

            if len(nodeConstraints[i]) > 1:
                print("Coincident nodes: ", str(nodeConstraints[i]))

        if self.seePlot.get():
            print("Close plot to continue simulation.")
            plot.basicPlot(nodeArray, system.getStringConn(), system.getBarConn())

        s0Percent: np.ndarray[np.ndarray[float]] = np.append(np.array([np.arange(1, len(csNew) + 1)]),
                                                             np.array([self.prestress.get() * np.ones(len(csNew), dtype=int)]), axis=0).T
        s0 = tkc.TensegPercentTo_s0(nNew, csNew, s0Percent)

        while len(self.forcesOnNodesArray[0]) < len(nNew[0]):
            self.forcesOnNodesArray = np.append(self.forcesOnNodesArray, np.array([[0, 0, 0]]).T, axis=1)

        while len(self.initialVelocities[0]) < len(nNew[0]):
            self.initialVelocities = np.append(self.initialVelocities, np.array([[0, 0, 0]]).T, axis=1)

        # Create data structure of system before segmentation.
        W = np.copy(self.forcesOnNodesArray)
        V = np.copy(self.initialVelocities)
        classKTest = ckt.ClassK_Test(nNew, cbNew, csNew, system, P, D, s0, V, W, dt=float(self.dtValueEntry.get()),
                                     tf=float(self.tfValueEntry.get()), axisLength=float(self.axisValueEntry.get()))
        classKTest.TensegSimClassKOpen(damping=float(self.dampingValueEntry.get()), updateForces=self.updateForces.get(), updateGround=self.useGround.get(),
                                       useController=self.useController.get())

        if self.haveVideo.get():
            SaveData.animateMotion(axisLength=classKTest.axisLength, barConn=classKTest.system.barConn, dt=classKTest.dt, nodeHist=classKTest.nodeHist,
                                   stringConn=classKTest.system.stringConn, tf=classKTest.tf, videoName=str(self.fileNameEntry.get()) + ".mp4")

        if self.makeFile.get():
            self.publishAsTextFile(classKTest)

        print("complete")

    @staticmethod
    def saveInfoAndClosePopup(currentWindow, varGrid, eGrid) -> None:
        """
        Saves the information from a popup window before closing it.
        :param currentWindow: The popup window
        :param varGrid: The variables in the popup window
        :param eGrid: The temporary entry variables in the popup window.
        :return: None
        """
        for i in range(1, len(eGrid)):
            for j in range(1, len(eGrid[0])):
                varGrid[i - 1][j - 1] = float(eGrid[i][j].get())

        currentWindow.destroy()

    @staticmethod
    def saveInfoAndClosePopupPinned(currentWindow, varGrid, eGrid):
        """
        saves the Information for the pinned node parameters
        :param currentWindow: The current popup.
        :param varGrid: The variable to change
        :param eGrid: The entry array that contains those changes.
        :return:
        """
        for i in range(0, len(eGrid)):
            varGrid[i] = float(eGrid[i].get())

        currentWindow.destroy()

    def surrogateAnimateMotion(self, optimizerModel, initialState, fileName):
        optimizerModel.tensModel.rk4(initialState)
        optimizerModel.tensModel.animateMotion(f"{fileName}.mp4")

    def updateNumBars(self, *args) -> None:
        """
        TODO: ensure that this works manually, mostly array orientations.
        Resets the variables that change when the number of bars change.
        :param args: arguments passed in.
        :return: None
        """
        try:
            newNumOfBars = int(self.numOfBarsEntry.get())
        except ValueError:
            return

        self.numOfBars.set(newNumOfBars)

        self.barConnectivityMatrix = np.zeros([self.numOfBars.get(), 2])

    def updateNumNodes(self, *args) -> None:
        """
        Resets the variables that change with the number of nodes changing.
        :param args: arguments passed in.
        :return: None
        """
        try:
            newNumOfNodes = int(self.numOfNodesEntry.get())
        except ValueError:
            return

        self.numOfNode.set(newNumOfNodes)

        self.coordinateNodeArray = np.zeros([self.numOfNode.get(), 3])
        self.forcesOnNodesArray = np.zeros([3, self.numOfNode.get()])
        self.initialVelocities = np.zeros([3, self.numOfNode.get()])

        try:
            newNumOfNodes = int(self.numOfNodesEntry.get())
        except ValueError:
            return

        self.numOfNode.set(newNumOfNodes)

    def updateNumPinned(self, *args) -> None:
        """
        Resets the variables that changes when the number of pinned nodes change.
        :param args: arguments
        :return: None
        """
        try:
            newNumOfPinnedNodes = int(self.numOfPinnedEntry.get())
        except ValueError:
            return

        self.numOfPinnedNode.set(newNumOfPinnedNodes)
        self.pinnedNodes = np.zeros([self.numOfPinnedNode.get()])

    def updateNumStrings(self, *args) -> None:
        """
        Resets the variables that would change if the number of strings changes.
        :param args: arguments
        :return: None
        """
        try:
            newNumOfStrings = int(self.numOfStringsEntry.get())
        except ValueError:
            return

        self.numOfStrings.set(newNumOfStrings)
        self.stringConnectivityMatrix = np.zeros([self.numOfStrings.get(), 2])

    def run(self) -> None:
        """
        The main method that runs the GUI.
        :return: None
        """
        nodeRow: int = 0

        nodeInfoText: tk.Label = tk.Label(self.root, height=3, width=40, font='Mistral 12 bold', text="Node Information:")
        nodeInfoText.grid(row=nodeRow, column=1)
        nodeInfoText.configure()

        numOfNodesText: tk.Label = tk.Label(self.root, height=3, width=40, text="Please enter the number of nodes in the system.")
        numOfNodesText.grid(row=nodeRow + 1, column=0)
        numOfNodesText.configure()

        self.numOfNodesEntry.delete(0, tk.END)
        self.numOfNodesEntry.insert(0, '3')
        self.numOfNodesEntry.grid(row=nodeRow + 1, column=1)

        self.numOfNode.trace_add("write", self.updateNumNodes)

        self.coordinateNodeArray = np.zeros([self.numOfNode.get(), 3])
        self.forcesOnNodesArray = np.zeros([self.numOfNode.get(), 3])
        self.initialVelocities = np.zeros([self.numOfNode.get(), 3])

        # These buttons use the XYZ variable function
        tk.Button(self.root, text="Change Node Coordinates", command=lambda: self.editVarsWithXYZ(varToChange=self.coordinateNodeArray, window=self.root,
                                                                                                  windowTitle="Specify Node Locations.")).grid(row=nodeRow + 2,
                                                                                                                                               column=0)
        tk.Button(self.root, text="Change Initial Node Velocities", command=lambda: self.editVarsWithXYZ(varToChange=self.initialVelocities.T, window=self.root,
                                                                                                         windowTitle="Specify Node Velocities.")).grid(
            row=nodeRow + 2,
            column=1)
        tk.Button(self.root, text="Change Forces on Nodes", command=lambda: self.editVarsWithXYZ(varToChange=self.forcesOnNodesArray.T, window=self.root,
                                                                                                 windowTitle="Specify Node Forces.")).grid(row=nodeRow + 2,
                                                                                                                                           column=2)

        connectionRow = nodeRow + 4
        connectionsTest: tk.Label = tk.Label(self.root, height=3, width=40, font='Mistral 12 bold', text="System Connections:")
        connectionsTest.grid(row=connectionRow, column=1)
        connectionsTest.configure()

        numOfBarsText: tk.Label = tk.Label(self.root, height=3, width=40, text="Please enter the number of bars in the system.")
        numOfBarsText.grid(row=connectionRow + 1, column=0)
        numOfBarsText.configure()

        self.numOfBarsEntry.delete(0, tk.END)
        self.numOfBarsEntry.insert(0, '2')
        self.numOfBarsEntry.grid(row=connectionRow + 1, column=1)

        self.numOfBars.trace_add("write", self.updateNumBars)

        tk.Button(self.root, text="Change barConnectivityMatrix", command=lambda: self.editPairedVars(varToChange=self.barConnectivityMatrix, window=self.root,
                                                                                                      windowTitle="Specify Bar Connections.")).grid(
            row=connectionRow + 1,
            column=2)
        numOfStringsText: tk.Label = tk.Label(self.root, height=3, width=40, text="Please enter the number of strings in the system.")
        numOfStringsText.grid(row=connectionRow + 2, column=0)
        numOfStringsText.configure()

        self.numOfStringsEntry.delete(0, tk.END)
        self.numOfStringsEntry.insert(0, '2')
        self.numOfStringsEntry.grid(row=connectionRow + 2, column=1)

        self.numOfStrings.trace_add("write", self.updateNumStrings)

        tk.Button(self.root, text="Change stringConnectivityMatrix",
                  command=lambda: self.editPairedVars(varToChange=self.stringConnectivityMatrix, window=self.root,
                                                      windowTitle="Specify String Connections.")).grid(
            row=connectionRow + 2,
            column=2)

        numOfPinnedText: tk.Label = tk.Label(self.root, height=3, width=40, text="Number of pinned Nodes:")
        numOfPinnedText.grid(row=connectionRow + 3, column=0)
        numOfPinnedText.configure()

        self.numOfPinnedEntry.delete(0, tk.END)
        self.numOfPinnedEntry.insert(0, '1')
        self.numOfPinnedEntry.grid(row=connectionRow + 3, column=1)

        self.numOfPinnedNode.trace_add("write", self.updateNumPinned)

        tk.Button(self.root, text="Change pinned nodes",
                  command=lambda:
                  self.editPinnedVars(varToChange=self.pinnedNodes, window=self.root, windowTitle="Specify Pinned Nodes.")).grid(row=connectionRow + 3,
                                                                                                                                 column=2)

        scalarValueRows: int = connectionRow + 5
        scalarText: tk.Label = tk.Label(self.root, height=3, width=40, font='Mistral 12 bold', text="Scalar Information:")
        scalarText.grid(row=scalarValueRows, column=1)
        scalarText.configure()

        dtValue: tk.Label = tk.Label(self.root, height=3, width=40, text="dt value")
        dtValue.grid(row=scalarValueRows + 1, column=0)
        dtValue.configure()

        self.dtValueEntry.insert(0, '.001')
        self.dtValueEntry.grid(row=scalarValueRows + 2, column=0)

        tfValue: tk.Label = tk.Label(self.root, height=3, width=40, text="tf value")
        tfValue.grid(row=scalarValueRows + 1, column=1)
        tfValue.configure()

        self.tfValueEntry.insert(0, '5')
        self.tfValueEntry.grid(row=scalarValueRows + 2, column=1)

        dampingValue: tk.Label = tk.Label(self.root, height=3, width=40, text="damping value")
        dampingValue.grid(row=scalarValueRows + 1, column=2)
        dampingValue.configure()

        self.dampingValueEntry.insert(0, '0.001')
        self.dampingValueEntry.grid(row=scalarValueRows + 2, column=2)

        prestressValue: tk.Label = tk.Label(self.root, height=3, width=40, text="prestress value")
        prestressValue.grid(row=scalarValueRows + 3, column=1)
        prestressValue.configure()
        self.prestressEntry.delete(0, tk.END)
        self.prestressEntry.insert(0, '0.7')
        self.prestressEntry.grid(row=scalarValueRows + 4, column=1)

        simulationOptionsRow: int = scalarValueRows + 6
        simulationOptions: tk.Label = tk.Label(self.root, height=3, width=40, font='Mistral 12 bold', text="Select Simulation Options:")
        simulationOptions.grid(row=simulationOptionsRow, column=1)
        simulationOptions.configure()

        self.nonConstForceCheckButton.grid(row=simulationOptionsRow + 1, column=0)
        self.useControllerCheckButton.grid(row=simulationOptionsRow + 1, column=2)
        self.useGroundCheckButton.grid(row=simulationOptionsRow + 1, column=1)

        run: tk.Button = tk.Button(self.root, text="Run Simulation", command=self.runSimulation)
        run.grid(row=simulationOptionsRow + 3, column=1)

        preConfiguredOptionsRow: int = 0
        preConfiguredOptions: tk.Label = tk.Label(self.root, height=3, width=40, font='Mistral 12 bold', text="Select Configuration to Load:")
        preConfiguredOptions.grid(row=preConfiguredOptionsRow, column=4)
        preConfiguredOptions.configure()

        dropDown: tk.OptionMenu = tk.OptionMenu(self.root, self.clicked, *self.options)
        dropDown.grid(row=preConfiguredOptionsRow + 1, column=4)

        tk.Button(self.root, text="load configuration", command=self.loadConf).grid(row=preConfiguredOptionsRow + 2, column=4)
        tk.Button(self.root, text="save current configuration", command=self.exportCurrentStateToFile).grid(row=preConfiguredOptionsRow + 1, column=5)
        tk.Button(self.root, text="imported saved configuration", command=self.importStateFromFile).grid(row=preConfiguredOptionsRow + 2, column=5)

        visualOptionRow = preConfiguredOptionsRow + 4
        visualOptionLabel: tk.Label = tk.Label(self.root, height=3, width=40, text="Select Display Options", font='Mistral 12 bold', justify='left')
        visualOptionLabel.grid(row=visualOptionRow, column=4, sticky='w')
        visualOptionLabel.configure()

        self.showPlotCheckButton.grid(padx=75, sticky='w', row=visualOptionRow + 1, column=4)
        self.createVideoCheckButton.grid(padx=75, sticky='w', row=visualOptionRow + 2, column=4)
        self.saveHistoryToFileCheckButton.grid(padx=75, sticky='w', row=visualOptionRow + 3, column=4)

        fileName: tk.Label = tk.Label(self.root, height=3, width=20, text="File Name", justify="left")
        fileName.grid(row=visualOptionRow + 4, column=4, sticky='w', padx=100)
        fileName.configure()

        self.fileNameEntry.insert(0, "default")
        self.fileNameEntry.grid(sticky='w', row=visualOptionRow + 5, column=4, padx=100)

        axisValue: tk.Label = tk.Label(self.root, height=3, width=20, text="Axis Size", justify="left")
        axisValue.grid(sticky='w', row=visualOptionRow + 6, column=4, padx=100)
        axisValue.configure()

        self.axisValueEntry.insert(0, '2')
        self.axisValueEntry.grid(sticky='w', row=visualOptionRow + 7, column=4, padx=100)

        tk.Button(self.root, text="Open surrogate model popup", command=self.openSurrogateModelPopup).grid(row=preConfiguredOptionsRow + 7, column=5)

        # Creates lines on the GUI for clarity.
        ttk.Separator(self.root, orient=tk.VERTICAL).grid(column=3, row=0, rowspan=simulationOptionsRow + 2, sticky='ns')
        ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(column=0, row=nodeRow + 3, columnspan=4, sticky='ew')
        ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(column=0, row=connectionRow + 4, columnspan=4, sticky='ew')
        ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(column=0, row=scalarValueRows + 5, columnspan=4, sticky='ew')
        ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(column=0, row=simulationOptionsRow + 2, columnspan=4, sticky='ew')
        ttk.Separator(self.root, orient=tk.HORIZONTAL).grid(column=4, row=preConfiguredOptionsRow + 3, columnspan=2, sticky='ew')

        self.root.mainloop()


if __name__ == "__main__":
    GUI = GUI()
    GUI.run()
