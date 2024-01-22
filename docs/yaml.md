# YAML Reference
The config file is a YAML file defining:
* [Nodes](#nodes)
* [Connections](#connections)
* [Pins](#pins) (optional)
* [Builders](#builders) (optional)

## Nodes
Nodes are the points that bars and strings connect at.

Nodes have a name and initial x, y, z positions.  
A node named `Node1` with x = 1, y = 2, and z = 0, it would look like:

```yaml
nodes:
    Node1: [1, 2, 0]
```


## Connections
Connections are how the nodes are connected to each other. There can be unlimited connection types, with each connection type having different properties as defined in the [Builders](#builders) section.

A connection type named `string` with a connection between `Node1` and `Node2` looks like:

```yaml
connections:
    string:
        - [Node1, Node2]
```

Connections can also optionally be named for later specifying connections to pin or to shorten.

```yaml
connections:
    string:
        - string1: [Node1, Node2] # Named connection
        - [Node2, Node3] # Unnamed connection
```

## Pins

## Builders
Builders are the connection properties that define the strings or bars that hold the nodes together.
A builder must have a name matching a connection type in the `Connections` section.

For the `string` connection type with a stiffness (k) of 100N/m (it is actually unitless, but it helps me to think of everything in terms of metric units) and the string tensioned to 5N this section would look like:


```yaml
builders:
    string:
        stiffness: 100
        pretension: 5
```

If the tension is unknown but the unstretched length of the string is known, Hooke's Law can be used to calculate the initial tension: $F = k * (l_s - l)$ where $l_s$ is the stretched length of the string (distance between it's nodes) and $l$ is the unstretched length.

If a connection type does not have a builder assigned to it, it is assumed to be a bar, which I define as a member being able to transfer force along its length, while not changing in length.