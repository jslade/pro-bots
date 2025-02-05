# pro-bots

A cient-server multi-player "game" to teach some programming concepts in a group setting

# Ideas

## Basic goal

Move a robot around a grid. Do things to earn points

can start off manually, then progressively add programs

## Robot

basic attributes of a robot:

- orientation
- energy
- colors: head, tail, ring

movement costs energy
collecting crystals gives energy, points

interacting with others gives points

obstacles that can be destroyed (attack requires energy)

energy regenerates when staying still

### Actions

- move forward, backward
- jump left or right (higher energy)
- rotate left or right
- inspect here, left, right, front, back
  -
- pickup (get enery, points)
- attack (front)
- say
- change color

### Programming

can move, etc interactively ("Command space" part of UI)
can write a program to automate ("Program space" part of UI)

programming is procedural and event-driven
programming is DSL, but can also be raw python? (sandboxed)

needs a "log" space as well to show incoming events

# Interface

client view is 3D
server view is top-down
