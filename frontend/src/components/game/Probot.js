import React, { useRef, useMemo } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Billboard, Text } from '@react-three/drei';
import { CrystalPlacement } from './Crystal';

const orientationAngle = (orientation) => {
    return {
        'E': 0,
        'N': Math.PI / 2,
        'W': Math.PI,
        'S': -Math.PI / 2,
    }[orientation] || 0;
}

const ProbotModel = ({ player, probot, ...props }) => {
    const meshRef = React.useRef()

    useFrame(() => {
        if (!meshRef.current) return;

        const angle = orientationAngle(probot.orientation)

        const proX = probot.x + probot.dx;
        const proY = 0.2;
        const proZ = -(probot.y + probot.dy);

        const rotX = 0;
        const rotY = angle + probot.dorient;
        const rotZ = 0;

        meshRef.current.position.set(proX, proY, proZ);
        meshRef.current.rotation.set(rotX, rotY, rotZ);
    });


  
    return (<mesh ref={meshRef}
            {...props}>
      
      <ExtrudedRing color={probot?.colors?.body}
        radius={0.38} tubeRadius={0.05}/>
      <ExtrudedDisc sweep={Math.PI*2} color={probot?.colors?.tail}
        radius={0.35} depth={0.035} />
      <ExtrudedDisc sweep={Math.PI} color={probot?.colors?.head}
        radius={0.30} depth={0.04} bevelSize={.05} bevelThickness={0.02}
        position={[0.02, 0.06, 0]} rotation={[0, Math.PI/2.0, 0]}
      />
      <EnergyRing energy={probot?.energy} color="red"
        innerRadius={0.45} outerRadius={0.52}
        thetaStart={Math.PI/2} thetaMax={Math.PI/2}
        position={[0, -0.04, 0]} rotation={[-Math.PI/2, 0, 0]} />
      <EnergyRing energy={probot?.crystals} color="blue"
        thetaStart = {0} thetaMax={Math.PI/2} reverse={true}
        innerRadius={0.45} outerRadius={0.52}
        position={[0, -0.0401, 0]} rotation={[-Math.PI/2, 0, -Math.PI/2]} />
      <Payload crystals={probot?.crystals} />
      {/*<InfoPanel message={player?.displayName} position={[0, 0.6, 0]} />*/}
    </mesh>)
};

function ExtrudedRing({
  sweep = Math.PI * 2,
  radius = 1,
  tubeRadius = 0.05,
  segments = 32,
  tubularSegments = 12,
  ...props
}) {
  const mesh = useRef();

  const geometry = useMemo(() => {
    // 1. Create the circular path using CatmullRomCurve3:
    const points = [];
    if (sweep === Math.PI * 2) { segments += 1; } // Close the circle
    for (let i = 0; i < segments; i++) {
      const angle = (i / segments) * sweep;
      const x = radius * Math.cos(angle);
      const z = radius * Math.sin(angle);
      points.push(new THREE.Vector3(x, 0, z)); // y = 0 for x/z plane
    }
    const path = new THREE.CatmullRomCurve3(points);


    // 2. Create the tube geometry:
    const geometry = new THREE.TubeGeometry(
      path,
      segments * 2, // More segments for smoother extrusion
      tubeRadius,
      tubularSegments,
      true // Closed path! Important!
    );

    return geometry;
  }, [radius, tubeRadius, segments, tubularSegments]);

  //useFrame(() => {
  //  mesh.current.rotation.y += 0.01;
  //});

  return (
    <mesh ref={mesh} geometry={geometry} {...props}>
      <meshStandardMaterial color={props?.color || "black"} />
    </mesh>
  );
}

const ExtrudedDisc = ({
  radius = 1,
  depth = 0.2,
  segments = 32,
  sweep = Math.PI * 2,
  bevelSegments = 1,
  bevelSize = 0.01,
  bevelThickness = 0.01,
  ...props
}) => {
  const mesh = useRef();

  const geometry = useMemo(() => {
    const shape = new THREE.Shape();
    shape.absarc(0, 0, radius, 0, sweep, false); // Create the disc shape
    if (sweep < Math.PI * 2) {
      shape.moveTo(0, 0);
    }

    const extrudeSettings = {
      steps: segments,
      depth: depth,
      bevelEnabled: true,
      bevelSegments: bevelSegments,
      bevelSize: bevelSize,
      bevelThickness: bevelThickness,
    };

    const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
    geometry.rotateX(Math.PI / 2); // Rotate to align with the YZ plane

    return geometry;
  }, [radius, depth, segments, bevelSize, bevelThickness, bevelSegments, sweep]);

  return (
    <mesh ref={mesh} geometry={geometry} {...props}>
      <meshStandardMaterial color={props?.color || "black"} />
    </mesh>
  );
};

function EnergyRing({
  energy,
  innerRadius = 1,
  outerRadius = 1.1,
  thetaSegments = 64,
  phiSegments = 1,
  thetaStart = 0,
  thetaMax = Math.PI / 2,
  reverse = false,
  color,
  ...props }) {
  const meshRef = useRef();

  const geometry = useMemo(() => {

    return new THREE.RingGeometry(innerRadius, outerRadius, thetaSegments, phiSegments, 0, 0);
  }, [innerRadius, outerRadius, phiSegments, thetaSegments]);

  useFrame(() => {
    // Update the ring geometry based on the energy value
    const newThetaLength = (energy / 1000) * thetaMax; // Assuming energy is between 0 and 100
    if (meshRef.current) {
      meshRef.current.geometry = new THREE.RingGeometry(
        innerRadius, outerRadius, thetaSegments, phiSegments,
        reverse ? thetaStart - newThetaLength : thetaStart, newThetaLength
      );
    }
  });

  return (
    <mesh ref={meshRef} {...props}>
      <primitive object={geometry} attach="geometry" />
      <meshPhysicalMaterial
        color={color}
        transparent={true}
        opacity={0.7}
      />
    </mesh>
  );
}

const InfoPanel = ({ message, ...props }) => {
  const textRef = useRef();

  return (
    <Billboard>
      <Text
        ref={textRef}
        position={[0, 0.3, 0]}
        fontSize={0.1}
        color="black"
        anchorX="center"
        anchorY="middle"
        rotation={[0, 0, 0]}
      >
        {message}
      </Text>
    </Billboard>
  );
}


const payloadPositions = [
  [0, 0, 0],
  [0.1, 0, 0.1],
  [-0.1, 0, 0.15],
  [0.1, 0, -0.12],
  [-0.09, 0, -0.13],
  [0.025, 0, 0.25],
  [-0.17, 0, -0.01],
  [-0.015, 0, -0.27],
  [0.14, 0, 0.25],
  [0.13, 0, -0.26],
  [-0.25, 0, 0.12],
  [0.10, 0, -0.42],
  [-0.08, 0, 0.40],
  [-0.08, 0, 0.40],
]
function Payload({ crystals, ...props }) {
  const groupRef = useRef();

  const groupPositions = Array.from({ length: Math.ceil(crystals / (1000 / payloadPositions.length)) }, (_, i) => 
    payloadPositions[i % payloadPositions.length]
  );

  return (
    <group ref={groupRef} position={[-0.15, 0.04, 0]} scale={[0.5, 0.5, 0.5]} {...props}>
      {groupPositions.map((position, index) => (
        <CrystalPlacement key={index} speed={1} position={position} />
      ))}
    </group>
  );
}


export default ProbotModel;
