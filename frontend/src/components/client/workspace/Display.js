import React from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import { GameContext } from '../../../contexts/GameContext';


import Ground from '../../game/Ground';
import ProbotModel from '../../game/Probot';

const Display = () => {
    const { gameState, probots, probot } = React.useContext(GameContext);

    return (
        <Canvas
            gl={{ alpha: false, antialias: true }}
            onCreated={({ gl }) => {
                gl.setClearColor('lightblue'); // Replace 'lightblue' with your desired color
            }}
         >
            {(gameState && probot) ? <DisplayScene
                gameState={gameState}
                grid={gameState.grid}
                probots={probots}
                probot={probot}
            /> : <></>}
        </Canvas>
    );
};

const orientationAngle = (orientation) => {
    return {
        'E': 0,
        'N': Math.PI / 2,
        'W': Math.PI,
        'S': -Math.PI / 2,
    }[orientation] || 0;
}

const DisplayScene = ({ gameState, grid, probots, probot }) => {
    return ( <>
        <ambientLight intensity={Math.PI / 2} />
        <spotLight position={[grid.width*2, grid.height*2, 10]} angle={0.15} penumbra={1} decay={0} intensity={Math.PI} />
        <pointLight position={[grid.width/2, grid.height*2, 2]} decay={0} intensity={Math.PI} />
        <Ground grid={gameState.grid} width={grid.width} height={grid.height} />
        {gameState.probots.map((p) => <ProbotModel key={p.name} probot={p} />)}
        <FollowingCamera probot={probot} />
{/*
        <OrbitControls />
*/}

    </>);
};

function FollowingCamera({ probot }) {
    const cameraRef = React.useRef();
  
    useFrame(() => {
        if (!cameraRef.current) return;

        const angle = orientationAngle(probot.orientation) + probot.dorient;

        const proX = probot.x + probot.dx;
        const proY = 0.2;
        const proZ = -(probot.y + probot.dy);

        const dist = 1.0;
        const cameraX = proX - dist * Math.cos(angle); 
        const cameraY = proY + 0.7;
        const cameraZ = proZ + dist * Math.sin(angle); 

        cameraRef.current.position.set(cameraX, cameraY, cameraZ);
        cameraRef.current.lookAt(proX, proY, proZ); // Look at the robot
    });
  
    return (
      <PerspectiveCamera
        ref={cameraRef}
        makeDefault
        position={[probot.x, probot.y, 0]}
        near={0.1}
        far={1000}
        fov={75}
      />
    );
  }
  
export default Display;
