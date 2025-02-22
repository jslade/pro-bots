import React, { useRef, useMemo } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';

const orientationAngle = (orientation) => {
    return {
        'E': 0,
        'N': Math.PI / 2,
        'W': Math.PI,
        'S': -Math.PI / 2,
    }[orientation] || 0;
}

const ProbotModel = ({ probot, ...props }) => {
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
      <EnergyRing energy={probot.energy} innerRadius={0.43} outerRadius={0.46}
        position={[0, -0.03, 0]} rotation={[Math.PI*1.5, 0, -Math.PI*1.5]} />
    </mesh>)
};

function ExtrudedRing({
  sweep = Math.PI * 2,
  radius = 1,
  tubeRadius = 0.05,
  segments = 64,
  tubularSegments = 16,
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
  segments = 64,
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
  thetaLength = Math.PI, // 180 degrees in radians

  ...props }) {
  const meshRef = useRef();

  const geometry = useMemo(() => {

    return new THREE.RingGeometry(innerRadius, outerRadius, thetaSegments, phiSegments, thetaStart, thetaLength);
  }, []);

  useFrame(() => {
    // Update the ring geometry based on the energy value
    const newThetaLength = (energy / 1000) * Math.PI; // Assuming energy is between 0 and 100
    if (meshRef.current) {
      meshRef.current.geometry = new THREE.RingGeometry(innerRadius, outerRadius, thetaSegments, phiSegments, 0, newThetaLength);
    }
  });

  return (
    <mesh ref={meshRef} {...props}>
      <primitive object={geometry} attach="geometry" />
      <meshPhysicalMaterial
        color="#ff0000"
        transparent={true}
        opacity={0.9}
      />
    </mesh>
  );
}
export default ProbotModel;
