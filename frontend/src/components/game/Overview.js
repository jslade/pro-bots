import React, { useContext, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { GameContext } from '../../contexts/GameContext';

const Overview = () => {
    const { gameState } = useContext(GameContext);

    return (
        <Canvas>
            <ambientLight intensity={Math.PI / 2} />
            <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} decay={0} intensity={Math.PI} />
            <pointLight position={[-10, -10, -10]} decay={0} intensity={Math.PI} />
            <Box position={[-1.2, 0, 0]} />
            <Box position={[1.2, 0, 0]} rotation={[1, 2, 3]} />
        </Canvas>
   );
};

function Box(props) {
    const meshRef = useRef()

    const [hovered, setHover] = useState(false)
    const [active, setActive] = useState(false)

    useFrame((state, delta) => {
        meshRef.current.rotation.x += delta;
        meshRef.current.rotation.y += delta * (active ? 1.5 : 0);
    })

    return (
      <mesh
        {...props}
        ref={meshRef}
        scale={active ? 1.5 : 1}
        onClick={(event) => setActive(!active)}
        onPointerOver={(event) => setHover(true)}
        onPointerOut={(event) => setHover(false)}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color={hovered ? 'hotpink' : 'orange'} />
      </mesh>
    )
}
  

export default Overview;
