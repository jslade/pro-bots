import React, { useContext } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { GameContext } from '../../contexts/GameContext';

import Ground from './Ground';
import ProbotModel from './Probot';

const Overview = () => {
    const { grid } = useContext(GameContext);

    if (!grid) return <></>;
    
    return (
        <Canvas>
            <DisplayStatic />
            <DisplayDynamic />
        </Canvas>
    );
};

const DisplayStatic = () => {
    const { grid } = useContext(GameContext);

    useThree(({ camera }) => {
        camera.position.set(grid.width / 2.0 - 0.5, grid.width * 0.58, - grid.height / 3.0 - 2);
        camera.rotation.set(-Math.PI / 2, 0.0, 0);
    })

    return ( <>
        <ambientLight intensity={Math.PI / 2} />
        <spotLight position={[grid.width*2, grid.height*2, 10]} angle={0.15} penumbra={1} decay={0} intensity={Math.PI} />
        <pointLight position={[grid.width/2, grid.height*2, 2]} decay={0} intensity={Math.PI} />
        <Ground grid={grid} />
    </>);
};

const DisplayDynamic = () => {
    const { pairs } = useContext(GameContext);

    if (!pairs?.map) return <></>;

    return ( <>
        {pairs.map((pp) => <ProbotModel key={pp.player.name} player={pp.player} probot={pp.probot} />)}
    </>);
};

export default Overview;
