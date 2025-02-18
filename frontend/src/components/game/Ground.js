import { lighten } from '@mui/material';
import React from 'react';

function Ground({ grid, width, height}) {
    const cells = [];
    for (let x = 0; x < width; x++) {
        for (let y = 0; y < height; y++) {
            const i = y*width + x;
            const cell = grid.cells[i];
            cells.push(<Cell key={`${x}-${y}`} x={x} y={y} cell={cell} />);
        }
    }
    return <>{cells}</>;
}

const cellColor = (cell) => {
    return lighten('#00aa00', cell.crystals / 100.0);
}

function Cell(props) {
    const meshRef = React.useRef()

    const [hovered, setHovered] = React.useState(false)

    const handleClick = React.useCallback(() => {
        console.log("clicked cell", props.cell);
    }, [props.cell]);
    
    return (
      <mesh
        {...props}
        ref={meshRef}
        position={[props.x, 0, -props.y]}
        onClick={(event) => handleClick()}
        onPointerOver={(event) => setHovered(true)}
        onPointerOut={(event) => setHovered(false)}>
        <boxGeometry args={[1, 0.1, 1]} />
        <meshStandardMaterial color={hovered ? 'hotpink' : cellColor(props.cell)} />
      </mesh>
    )
}

export default Ground;