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
    </mesh>)
};

function ExtrudedRing({
  radius: radius = 1,
  tubeRadius = 0.05,
  segments = 64,
  tubularSegments = 16,
  ...props
}) {
  const mesh = useRef();

  const geometry = useMemo(() => {
    // 1. Create the circular path using CatmullRomCurve3:
    const points = [];
    for (let i = 0; i <= segments; i++) {  // Include the last point to close the circle
      const angle = (i / segments) * 2 * Math.PI;
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

  useFrame(() => {
    mesh.current.rotation.y += 0.01;
  });

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

export default ProbotModel;
