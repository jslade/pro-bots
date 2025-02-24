import React, { useRef, useMemo } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { MeshDistortMaterial } from '@react-three/drei';

function Crystal({ color, radius = 0.02, length = 0.08, facets=6, ...props }) {
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
            <MeshDistortMaterial
                color={color}
                transparent={true}
                opacity={0.8}
                distort={0.1}
                speed={0}
            />
        </mesh>
    );
}

function CrystalGroup({ count, speed=1, position, ...props }) {
    const group = useRef();

    useFrame(() => {
        group.current.rotation.x += 0.005 * speed;
        group.current.rotation.y += 0.004 * speed;
        group.current.rotation.z += 0.003 * speed;
    });

    const crystals = Array.from({ length: count }, (_, i) => {
        const facets = 4 + Math.floor(Math.random() * 4) ;
        const radius = 0.02 + Math.random() * 0.01;
        const length = radius * (6 + Math.random()) * 0.5;
        const angleX = (i/count) * Math.PI * 2 + Math.random() * 0.5;
        const angleY = (i/count) * Math.PI * 2 + Math.random() * 0.5;
        const angleZ = 0;
        const offsetX = 0;
        const offsetY = 0;
        const offsetZ = 0;
        const color = new THREE.Color(Math.random(), Math.random(), Math.random()).getStyle(); // Random color

        return (
            <Crystal
            key={i}
            facets={facets}
            color={color}
            radius={radius}
            length={length}
            position={[offsetX, offsetY, offsetZ]}
            rotation={[angleX, angleY, angleZ]}
            {...props}
            />
        );
        });

    return ( <group ref={group} position={position}>
        {crystals}
    </group> );
}

export { Crystal, CrystalGroup };
