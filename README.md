# pro-bots

A client-server multi-player "game" to teach some programming concepts in a group setting

## Vision for how it will be used:

The experience should be something like:

- I do a very brief intro about programming, 5 min
- Demo the tool, 5 min
- every gets a laptop already connected to the church wi-fi
- enter the ip address and join -- just enter a username

So hopefully within 15 minutes or so of starting, everyone is connected and can immediately begin interacting.

- client view consists of 3d "3rd person" view of their "Probot", plus a code editor pane and a terminal pane
- they can interact with the Probot immediately using a few simple controls (move forward, turn)
- to do more interesting things, they can use the terminal
- then to start getting complex behaviors and automating the Probot, need to actually write some multi-line scripts in the code editor

Total time for the activity is a little more than an hour, so I want them to have hands on their own keyboards and start playing as quickly as possible.

# Ideas

## Basic goal

Move a robot around a grid. Do things to earn points

- collecting crystals
- interacting with others
- complexity of programs

Can start off manually, then progressively add programming

## Robot

basic attributes of a robot:

- orientation
- energy
- colors: head, tail, ring

movement costs energy
collecting crystals gives energy, points

interacting with others gives points

obstacles that can be destroyed (attack requires energy)

energy regenerates when idle

### Actions

- move forward, backward
- jump left or right (higher energy)
- rotate left or right
- ## inspect here, left, right, front, back
- pickup (get energy, points)
- attack (front) (???)
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
server (watcher) view is top-down

# Tech stack

## General

Frontend written in React, three.js

Backend written in python/Flask

Communication is primarily websockets, with a bit of http for the initial handshake

docker-compose for simple deployment

## Programming

Using [TatSu](https://tatsu.readthedocs.io/en/stable/intro.html) to generate the parser from a custom [grammar](https://github.com/jslade/pro-bots/wiki/Probotics).

I'll most likely implement an custom interpreter directly in python. I haven't come across any good tools to leverage for that yet.

# Programming language

[Probotics](https://github.com/jslade/pro-bots/wiki/Probotics) is the name of the language I'm planning to implement. Mostly based on elements from python, ruby, javascript.

# Usage / Deployment

At least for the initial usage, I plan to just deploy on a raspberry pi running docker, and have all the kids connect from laptops directly via ip address.

## Equipment

- Server: Raspberry Pi 4
- Clients: Any modern browser, ideally every participant on an individual laptop (keyboards needed, mouse optional)
- Large-screen TV: "watcher" view for everyone to follow (connected from my personal laptop, or could be chromecast or something from the rpi)


# TODO

[ ] auto-wait during movement
[ ] builtins: `jump`, `collect`, `inspect`,  `say`,
[ ] event-driven programs
[ ] scripts for bots
[ ] documentation / reference materials
[ ] admin stuff: game reset, password reset
[ ] visual improvements in 3d view
[ ] code syntax highlighting
[ ] audio effects
[ ] game end conditions - high score
[ ] cookie to retain login session

