import React, { useContext, useEffect, useState } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { GameContext } from '../../contexts/GameContext';

import Ground from './Ground';
import ProbotModel from './Probot';

const Overview = () => {
    const { gameState, pairs } = useContext(GameContext);

    const [width, setWidth] = useState(1);
    const [height, setHeight] = useState(1);

    useEffect(() => {
        if (!gameState) return;

        const grid = gameState.grid;
        setWidth(grid.width);
        setHeight(grid.height);

    }, [gameState, gameState?.grid]);

    return (
        <Canvas>
            {gameState ? <OverviewScene
                gameState={gameState}
                pairs={pairs}
                width={width}
                height={height}
            /> : <></>}
        </Canvas>
    );
};

const OverviewScene = ({ gameState, pairs, width, height }) => {
    useThree(({ camera }) => {
        camera.position.set(width / 2.0 - 0.5, width * 0.58, - height / 3.0 - 2);
        camera.rotation.set(-Math.PI / 2, 0.0, 0);
    })

    return ( <>
        <ambientLight intensity={Math.PI / 2} />
        <spotLight position={[width*2, height*2, 10]} angle={0.15} penumbra={1} decay={0} intensity={Math.PI} />
        <pointLight position={[width/2, height*2, 2]} decay={0} intensity={Math.PI} />
        <Ground grid={gameState.grid} width={width} height={height} />
        {pairs.map((pp) => <ProbotModel key={pp.player.name} player={pp.player} probot={pp.probot} />)}
    </>);
};

export default Overview;
