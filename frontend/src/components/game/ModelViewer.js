import React from 'react';
import { Grid, Box } from '@mui/material';
import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';

import ProbotModel from './Probot';

const viewPlayer = {
    "name": "bot-0",
    "displayName": "Bot 0",
    "score": 12345,
    "colors": {
        "body": "#404040",
        "head": "darkred",
        "tail": "midnightblue"
    },
    "programState": "running"
}

const viewProbot = {
    "player": "bot-0",
    "colors": {
        "body": "#404040",
        "head": "darkred",
        "tail": "midnightblue"
    },
    "id": 0,
    "name": "bot-0",
    "x": 0,
    "y": 0,
    "orientation": "W",
    "state": "idle",
    "energy": 1000,
    "crystals": 1000,
    "dx": 0,
    "dy": 0,
    "dorient": 0,
};

const ModelViewer = () => {
    return (
        <Grid container spacing={0} style={{ height: '100vh', width: '100vw' }}>
            <Grid item xs={12}>
                <Box display="flex" flexDirection="width" height="100%">
                    <ViewerCanvas />
                </Box>
            </Grid>
        </Grid>
    );
};

const ViewerCanvas = () => {
    return (
        <Canvas
            gl={{ alpha: false, antialias: true }}
            onCreated={({ gl }) => {
                gl.setClearColor('lightblue');
            }}
        >
            <ViewerCanvasContent player={viewPlayer} probot={viewProbot}/>
            <OrbitControls />
        </Canvas>
    )
};

const ViewerCanvasContent = ({ player, probot }) => {
    useThree(({ camera }) => {
        camera.position.set(1.0, 1.0, 0);
        camera.lookAt([0, 0, 0]);
    })

    return ( <>
        <ambientLight intensity={Math.PI / 2} />
        <spotLight position={[40, 40, 10]} angle={0.15} penumbra={1} decay={0} intensity={Math.PI} />
        <pointLight position={[10, 20, 2]} decay={0} intensity={Math.PI} />
        <ProbotModel player={player} probot={probot} />
    </>);
};

export default ModelViewer;
