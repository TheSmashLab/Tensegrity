# Linked Nodes
In preperation for wrapping nodes around a surface, I am adding the ability to link nodes on opposite edges.  
Currently nodes must be linked so the structure is wrapped around a $\hat{k}$ axis. In other words the x-axis wraps the circumference of the cylinder with a set radius, r. In the future I hope we can define the radius to change as a function of the z height, either with an equation, or reading in points from a file and using interpolation.

## Todo
- [x] Decide yaml format
- [x] Add to yaml_parser
  - [x] Update data_structures
- [x] If string passes through linked nodes, distance is 0
- [x] x distance between linked nodes must stay fixed (the circumference of the cylinder) 
- [x] y value of linked nodes is the same
- [x] Forces: combine y forces and remove second node from force equations
- [x] Don't analyze x forces on seam??? Force needs to be applied to pull it apart
- [x] Update viz for 3D???
- [ ] Fix lengths of strings to follow curve of cylinder
- [ ] Fix bugs

## Config File
```yaml
surface:
  cylinder:
    radius: 3.5

  linked_nodes:
    - [Node1, Node7]
    - [Node4, Node8]
    - [Node9, Node12]
```
The only currently defined surface for linking nodes around is a cylinder.