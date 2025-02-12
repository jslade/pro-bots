import React from 'react';

const ProbotModel = ({ probot, ...props }) => {
    const meshRef = React.useRef()

    const position = [probot.x + probot.dx, 0.1, -(probot.y + probot.dy)];

    return (<mesh ref={meshRef}
            scale={[0.4, 0.4, 0.4]}
            position={position}
            {...props}>
        {/* Outer ring (body of the robot) */}
        <cylinderGeometry args={[1, 1, 0.5, 32]} />
        <meshStandardMaterial color="red" />
  
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
