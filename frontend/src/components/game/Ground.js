import { lighten } from '@mui/material';
import React, { useMemo } from 'react';

import { CrystalPlacement } from './Crystal';

function Ground({ grid }) {
    const groundRef = React.useRef();

    const renderCells = useMemo(() => {
        const cells = [];
        for (let x = 0; x < grid.width; x++) {
            for (let y = 0; y < grid.height; y++) {
                const i = y*grid.width + x;
                const cell = grid.cells[i];
                cells.push(<Cell key={`${x}-${y}`} x={x} y={y} cell={cell} />);
            }
        }
        return cells;
    }, [grid]);

    return (
        <group ref={groundRef}>
            {renderCells}
        </group>
    );
}

const cellColor = (cell) => {
    return lighten('#004400', cell.crystals / 2000.0);
}

function Cell(props) {
    const meshRef = React.useRef()

    const [hovered, setHovered] = React.useState(false)

    const handleClick = React.useCallback(() => {
        console.log("clicked cell", props.cell);
    }, [props.cell]);
    
    return ( <>
        <mesh
            {...props}
            ref={meshRef}
            position={[props.x, -0.5, -props.y]}
            onClick={(event) => handleClick()}
            onPointerOver={(event) => setHovered(false)}
            onPointerOut={(event) => setHovered(false)}>
            <boxGeometry args={[1, 1, 1]} />
            <meshStandardMaterial color={hovered ? 'hotpink' : cellColor(props.cell)} />
        </mesh>
        {<GroundCrystals crystals={props.cell.crystals} position={[props.x, 0.0, -props.y]} scale={[]} />}
        </>
    )
}

const crystalPositions = [
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
function GroundCrystals({ crystals, ...props }) {
    const groupRef = React.useRef();

    const rendered = useMemo(() => {
        const groupPositions = Array.from({ length: Math.ceil(crystals / (5000 / crystalPositions.length)) }, (_, i) => 
            crystalPositions[i % crystalPositions.length]
        );
        
        return Array.from({ length: Math.ceil(crystals / 500) }, (_, i) => 
            <CrystalPlacement key={i} position={groupPositions[i % groupPositions.length]} speed={0}/>
        );
    }, [crystals]);

    return (
        <group ref={groupRef} {...props}>
            {rendered}
        </group>
    );
}

export default Ground;