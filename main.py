import numpy as np
import tkinter
import math
from PIL import ImageGrab
import random

imagecount = 0

'''
3x3 matrix multiplication helper functions
'''
def rotx(theta):
    S = math.sin(theta)
    C = math.cos(theta)
    return np.array([[1, 0, 0], [0, C, -S], [0, S, C]])
def roty(theta):
    S = math.sin(theta)
    C = math.cos(theta)
    return np.array([[C, 0, S], [0, 1, 0], [-S, 0, C]])
def rotz(theta):
    S = math.sin(theta)
    C = math.cos(theta)
    return np.array([[C, -S, 0], [S, C, 0], [0, 0, 1]])

'''
Takes in an input of a shape (list of vertices and edges) and a truncation factor
and returns a new shape that has been truncated
'''
def truncate(shape, t):
    shape_new = [0,0]
    nbr_cnt = [0] #this will be an array containing the partial sums of the degrees of each vertex
    sum=0
    for v in range(len(shape[1])):
        sum += len(shape[1][v])
        nbr_cnt += [sum]

    vertices_new = []
    for v in range(len(shape[1])):
        for w in shape[1][v]:
            vertices_new += [(1-t)*shape[0][v]+(t)*shape[0][w]] #adds the new vertices from truncation using the truncation parameter
    shape_new[0]=np.array(vertices_new)

    edges_new = []
    for i in range(len(nbr_cnt)-1):
        for j in range(nbr_cnt[i+1]-nbr_cnt[i]):
            #we are indexing through the vertices by using the nbr_cnt array.
            #each iteration of the nested for loop can be treated as iterating through the truncated face of a vertex
            #in this loop we are connecting one truncated face to its adjacent truncated face
            edges_new += [[]]
            v = i
            w = shape[1][v][j]
            edges_new[-1] += [nbr_cnt[w]+np.where(shape[1][w] == v)[0][0]]
    for i in range(len(nbr_cnt)-1):
        for j in range(nbr_cnt[i],nbr_cnt[i+1]):
            #same thing as before, but this time we are connecting together a single truncated face
            #for each vertex of the truncated face, we find the closest vertices. Those will be the neighbors of the polygon
            v = shape_new[0][j]
            mindist = [math.inf,math.inf]
            mink = [0,0]
            for k in range(nbr_cnt[i],nbr_cnt[i+1]):
                w = shape_new[0][k]
                if(k != j and dist(v,w) < mindist[1]):
                    if(dist(v,w) < mindist[0]):
                        mindist[1] = mindist[0]
                        mindist[0] = dist(v,w)
                        mink[1]=mink[0]
                        mink[0]=k
                    else:
                        mindist[1] = dist(v,w)
                        mink[1]=k
            edges_new[j] += [mink[0]]
            edges_new[j] += [mink[1]]
    
    shape_new[1] = np.array(edges_new)


    return shape_new

#returns the distance between two points in 3d space
def dist(A, B):
    total = 0
    for i in range(3):
        total += (A[i]-B[i]) ** 2
    return math.sqrt(total)

#helper function that draws an edge between two points
def connectEdge(A, B, canvas):
    canvas.create_line(A[0], A[1], B[0], B[1], width = 5)
    return
#draws a shape using the vertex list and adjacency list
def draw(shape, canvas):
    for v in range(len(shape[1])):
        for w in shape[1][v]:
            connectEdge(shape[0][v], shape[0][w], canvas)
    return

size=400
root = tkinter.Tk()
canvas = tkinter.Canvas(root, height=2*size, width=2*size)
canvas.configure(bd=0,highlightthickness=0)
canvas.configure(scrollregion=(-size, -size, size, size))
canvas.pack()

shape=[0,0]


#instructions to make cube
vertices= []
for i in [-1,1]:
    for j in [-1,1]:
        for k in [-1,1]:
            vertices += [[i * size/2,j * size/2,k * size/2]]
vertices = np.array(vertices)
shape[0] = vertices

edges = []
precision = 50
for v in range(len(shape[0])):
    edges+= [[]]
    for w in range(len(shape[0])):
        if(abs(dist(shape[0][v], shape[0][w])-size)<= precision):
            edges[v] += [w]
edges = np.array(edges, dtype=object)
shape[1] = edges            

#rotates it to a presentable angle
for i in range(len(shape[0])):
    shape[0][i] = np.matmul(roty(-1*math.pi/5),shape[0][i])



#function that saves the tkinter view to a png
def save(widget, name):
    x=root.winfo_rootx()+widget.winfo_x()
    y=root.winfo_rooty()+widget.winfo_y()
    x1=x+1100
    y1=y+1000
    ImageGrab.grab().crop((x+100,y,x1,y1)).save("pics/"+name+".png")


def redraw():
    global imagecount
    canvas.delete("all")
    canvas.after(100, redraw) #.1 seconds between drawings
    imagecount += 1
    save(canvas, str(imagecount))

    #does a conjugated rotation
    for i in range(len(shape[0])):
        shape[0][i] = np.matmul(roty(1*math.pi/5),shape[0][i])
        shape[0][i] = np.matmul(rotx(2*math.pi/60),shape[0][i])
        shape[0][i] = np.matmul(roty(-1*math.pi/5),shape[0][i])
    
    #trialled and errored to create a function that returns a triangle wave with period 2p and range from 0 to .5
    #desmos: https://www.desmos.com/calculator/uzgvdvwvio
    modfunc = lambda x,p : .5*((x % (2*p))-(2/p)*(x % p)*((x % (2*p))-(x % p)))/p
    
    draw(truncate(shape,modfunc(imagecount,30)), canvas)
canvas.after(2000, redraw) #waits 2 seconds before starting to draw
root.mainloop()