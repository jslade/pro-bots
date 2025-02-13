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
      <ExtrudedRing color={probot?.colors?.body} />
      <Canopy color={probot?.colors?.head}
        position={[0.15, 0.05, -0.05]} />
    </mesh>)
};

function ExtrudedRing({
  pathRadius = 0.30,
  tubeRadius = 0.1,
  segments = 32,
  tubularSegments = 4,
  ...props
}) {
  const mesh = useRef();

  const geometry = useMemo(() => {
    // 1. Create the circular path using CatmullRomCurve3:
    const points = [];
    for (let i = 0; i <= segments; i++) {  // Include the last point to close the circle
      const angle = (i / segments) * 2 * Math.PI;
      const x = pathRadius * Math.cos(angle);
      const z = pathRadius * Math.sin(angle);
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
  }, [pathRadius, tubeRadius, segments, tubularSegments]);

  return (
    <mesh ref={mesh} geometry={geometry} {...props}>
      <meshStandardMaterial color={props?.color || "black"} />
    </mesh>
  );
}

function Canopy({ width = .2, height = .1, depth = .1, segments = 32, ...props }) {
  const mesh = useRef();

  const geometry = useMemo(() => {
    const shape = new THREE.Shape();

    // Define the canopy profile (adjust these points to change the shape)
    shape.moveTo(0, 0);
    shape.lineTo(-width, 0);
    shape.lineTo(-width, height);
    //shape.lineTo(width * 0.9, height * 0.8); // Slightly curved top
    //shape.lineTo(width * 0.1, height * 0.8); // Slightly curved top
    shape.lineTo(0, 0);

    const extrudeSettings = {
      steps: segments,
      depth: depth,
      bevelEnabled: true,
    };

    return new THREE.ExtrudeGeometry(shape, extrudeSettings);
  }, [width, height, depth, segments]);

  useFrame(({ clock }) => {
    // Optional: Add some subtle animation
    mesh.current.rotation.y = Math.sin(clock.getElapsedTime() * 0.1) * 0.05;
  });

  return (
    <mesh ref={mesh} geometry={geometry} {...props}>
      <meshStandardMaterial color={props.color || "black"} />
    </mesh>
  );
}

export default ProbotModel;
