import React from 'react';
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
        const rotY = angle;
        const rotZ = 0;

        meshRef.current.position.set(proX, proY, proZ);
        meshRef.current.rotation.set(rotX, rotY, rotZ);
    });
  
    return (<mesh ref={meshRef}
            scale={[0.5, 0.4, 0.3]}
            {...props}>
        {/* Outer ring (body of the robot) */}
        <cylinderGeometry args={[1, 1, 0.5, 32]} />
        <meshStandardMaterial color="gray" />
  
        {/* Front part (like a cockpit window) */}
        <mesh position={[0, 0, 0.25]}>
          <sphereGeometry args={[0.7, 32, 16, 0, Math.PI * 2, 0, Math.PI / 3]} />
          <meshStandardMaterial color="blue" />
        </mesh>
  
        {/* Rear parts (like a pickup bed) */}
        <mesh position={[0, 0, -0.25]}>
          <cylinderGeometry args={[0.7, 0.7, 0.2, 32, 1, true, 0, Math.PI]} />
          <meshStandardMaterial color="green" />
        </mesh>
        <mesh position={[0, 0, -0.25]} rotation={[0, Math.PI, 0]}>
          <cylinderGeometry args={[0.7, 0.7, 0.2, 32, 1, true, 0, Math.PI]} />
          <meshStandardMaterial color="green" />
        </mesh>
    </mesh>)
};

export default ProbotModel;
