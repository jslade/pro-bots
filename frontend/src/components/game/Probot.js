import React, { useRef, useMemo } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { CrystalPlacement } from './Crystal';

const orientationAngle = (orientation) => {
    return {
        'E': 0,
        'N': Math.PI / 2,
        'W': Math.PI,
        'S': -Math.PI / 2,
    }[orientation] || 0;
}

const energyRings = [];
const crystalRings = [];

for (const i of Array.from({ length: 1001 }, (_, i) => i)) {
  energyRings.push(<EnergyRing energy={i} color="red"
    innerRadius={0.45} outerRadius={0.52}
    thetaStart={Math.PI/2} thetaMax={Math.PI/2}
    position={[0, -0.04, 0]} rotation={[-Math.PI/2, 0, 0]} />);
  crystalRings.push(<EnergyRing energy={i} color="blue"
    thetaStart = {0} thetaMax={Math.PI/2} reverse={true}
    innerRadius={0.45} outerRadius={0.52}
    position={[0, -0.0401, 0]} rotation={[-Math.PI/2, 0, -Math.PI/2]} />);
}

const programStateSize = 0.05;

const StateCube = ({ color, ...props }) => {
  const meshRef = useRef();

  React.useEffect(() => {
    if (!meshRef.current) return;

    return () => {
      meshRef.current?.geometry.dispose();
      meshRef.current?.material.dispose();
    }
  }, []);

  return (
    <mesh ref={meshRef} position={[0.15, 0.08, 0]} {...props}>
      <boxGeometry args={[programStateSize, programStateSize, programStateSize]} />
      <meshStandardMaterial color={color} />
    </mesh>
  );
};

const programStates = {
  "running": <StateCube color="#55ff55" />,
  "paused": <StateCube color="cyan" />,
  "not_running": <StateCube color="red" />,
}

const ProbotModel = ({ player, probot, ...props }) => {
    const probotMeshRef = React.useRef()

    useFrame(() => {
        if (!probotMeshRef.current) return;

        const angle = orientationAngle(probot.orientation)

        const proX = probot.x + probot.dx;
        const proY = 0.2;
        const proZ = -(probot.y + probot.dy);

        const rotX = 0;
        const rotY = angle + probot.dorient;
        const rotZ = 0;

        probotMeshRef.current.position.set(proX, proY, proZ);
        probotMeshRef.current.rotation.set(rotX, rotY, rotZ);
    });

    const baseGeometry = useMemo(() => {
      if (!probot?.colors) return null;

      return <>
        <ExtrudedRing color={probot.colors.body}
          radius={0.38} tubeRadius={0.05}/>
        <ExtrudedDisc sweep={Math.PI*2} color={probot.colors.tail}
          radius={0.35} depth={0.035} />
        <ExtrudedDisc sweep={Math.PI} color={probot.colors.head}
          radius={0.30} depth={0.04} bevelSize={.05} bevelThickness={0.02}
          position={[0.02, 0.06, 0]} rotation={[0, Math.PI/2.0, 0]}
        />
      </>
    }, [probot?.colors]);

    const programState = useMemo(() => {
      if (!player?.programState) return null;
      return programStates[player?.programState];
    }, [player?.programState]);

    const energyRing = useMemo(() => {
      if (!probot?.energy) return null;
      return energyRings[probot?.energy];
    }, [probot?.energy]);

    const crystalRing = useMemo(() => {
      if (!probot?.crystals) return null;
      return crystalRings[probot?.crystals];
    }, [probot?.crystals]);

    const payload = useMemo(() => {
      if (!probot?.crystals) return null;
      return (probot?.crystals > 0) && <Payload crystals={1} />
    }, [probot?.crystals]);

    const collecting = useMemo(() => {
      if (probot?.state !== "collecting") return null;
      return <CollectingCone />
    }, [probot?.state]);

    const saying = useMemo(() => {
      if (probot?.state !== "saying") return null;
      return <SpeakingCone />
    }, [probot?.state]);

    return (<mesh ref={probotMeshRef}
            {...props}>
      {baseGeometry}
      {programState}
      {energyRing}
      {crystalRing}
      {payload}
      {collecting}
      {saying}

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
    const full = sweep === Math.PI * 2;
    for (let i = 0; i < segments + (full ? 1 : 0); i++) {
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
  }, [sweep, radius, tubeRadius, segments, tubularSegments]);

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
    const thetaLength = (energy / 1000) * thetaMax;
    return new THREE.RingGeometry(
      innerRadius, outerRadius, thetaSegments, phiSegments,
      reverse ? thetaStart - thetaLength : thetaStart, thetaLength
    );
  }, [
    innerRadius, outerRadius, phiSegments, thetaSegments,
    energy, reverse, thetaStart, thetaMax
  ]);

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


const CollectingCone = () => {
  const meshRef = useRef();
  const scaleRef = useRef(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      scaleRef.current = (scaleRef.current + 0.2) % 1;
    }, 800);

    return () => {
      clearInterval(interval);
      meshRef?.current?.geometry.dispose();
      meshRef?.current?.material.dispose();
    }
  }, []);

  useFrame(() => {
    if (!meshRef.current) return;
    meshRef.current.scale.set(1, scaleRef.current, 1);
    scaleRef.current = (scaleRef.current + 0.01) % 1;
  });

  return (
    <mesh ref={meshRef} position={[-0.1, -0.18, 0]}>
      <coneGeometry args={[0.35, 0.4, 32]} />
      <meshStandardMaterial color="grey" transparent opacity={0.5} />
    </mesh>
  );
};


const SpeakingCone = () => {
  const meshRef = useRef();
  const scaleRef = useRef(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      scaleRef.current = (scaleRef.current + 0.2) % 1;
  }, 300);

    return () => {
      clearInterval(interval);
      meshRef?.current?.geometry.dispose();
      meshRef?.current?.material.dispose();
    }
  }, []);

  useFrame(() => {
    if (!meshRef.current) return;
    meshRef.current.scale.set(1, scaleRef.current, 1);
    scaleRef.current = (scaleRef.current + 0.05) % 1;
  });

  return (
    <mesh ref={meshRef} position={[0.5, 0, 0]} rotation={[0, 0, Math.PI/2]}>
      <coneGeometry args={[0.1, 0.35, 32]} />
      <meshStandardMaterial color="yellow" transparent opacity={0.5} />
    </mesh>
  );
};


export default ProbotModel;
