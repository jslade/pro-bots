import React, { useRef, useMemo } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';

function Crystal({ color, radius = 0.02, length = 0.08, facets=4, ...props }) {
    const geometry = useMemo(() => {
        const shape = new THREE.Shape();

        for (let i = 0; i < facets; i++) {
            const angle = (i / facets) * Math.PI * 2;
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;
            if (i === 0) shape.moveTo(x, y);
            else shape.lineTo(x, y);
        }
        shape.closePath();

        const extrudeSettings = {
            steps: 1,
            depth: length,
            bevelEnabled: false,
        };

        return new THREE.ExtrudeGeometry(shape, extrudeSettings);
    }, [facets, length, radius]);

    return (
        <mesh geometry={geometry} {...props} >
            <meshStandardMaterial color={color} />
        </mesh>
    );
}

// Only generate a fixed number of crystals and reuse them
// This is to avoid creating new geometries and materials every frame
// This is a performance optimization
// The number of crystals is arbitrary, you can adjust it to your needs
const crystalCount = 100;
const crystalCache = [];

for (let i = 0; i < crystalCount; i++) {
    const facets = 4 ;//+ Math.floor(Math.random() * 3) ;
    const radius = 0.02 + Math.random() * 0.01;
    const length = radius * (6 + Math.random()) * 0.5;
    const color = new THREE.Color(Math.random(), Math.random(), Math.random()).getStyle(); // Random color

    crystalCache.push(
        <Crystal facets={facets} radius={radius} length={length} color={color} />
    );
}

function CrystalGroup({ count=5, ...props }) {
    const group = useRef();

    const crystals = useMemo(() => {
        return Array.from({ length: count }, (_, i) => {
            const angleX = (i/count) * Math.PI * 2 + Math.random() * 0.5;
            const angleY = (i/count) * Math.PI * 2 + Math.random() * 0.5;
            const angleZ = 0;
            const index = Math.floor(Math.random() * crystalCount);

            return (
                <mesh key={i}
                    rotation={[angleX, angleY, angleZ]}>
                    {crystalCache[index]}
                </mesh>
            );
        });
    }, [count]);
    return ( <group ref={group} {...props}>
        {crystals}
    </group> );
}

// Only generate a fixed number of crystal groups and reuse them
// This is to avoid creating new geometries and materials every frame
// This is a performance optimization
const crystalGroupCount = 20;
const crystalGroupCache = [];

for (let i = 0; i < crystalGroupCount; i++) {
    const count = 5 + Math.floor(Math.random() * 2);
    crystalGroupCache.push(<CrystalGroup count={count} key={i} />);
}   

function CrystalPlacement({speed=1, ...props}) {
    const group = useRef();
    const crystals = useMemo(() => {
        const index = Math.floor(Math.random() * crystalGroupCount);
        const rotation = [Math.random() * Math.PI * 2, Math.random() * Math.PI * 2, Math.random() * Math.PI * 2];

        return <mesh rotation={rotation}>
            {crystalGroupCache[index]}
        </mesh>
    }, []);

    useFrame(() => {
        if (speed === 0) return;
        
        group.current.rotation.x += 0.005 * speed;
        group.current.rotation.y += 0.004 * speed;
        group.current.rotation.z += 0.003 * speed;
    });

    return (
        <group ref={group} {...props}>
            {crystals}
        </group>
    );
}

export { Crystal, CrystalGroup, CrystalPlacement };
