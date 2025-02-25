import React, { useEffect } from 'react';
import Stats from 'stats.js';

const StatsComponent = ({stat=0}) => {
    useEffect(() => {
        const stats = new Stats();
        stats.showPanel(stat); // 0: fps, 1: ms, 2: mb, 3+: custom
        document.body.appendChild(stats.dom);

        const animate = () => {
        stats.begin();
        stats.end();
        requestAnimationFrame(animate);
        };

        requestAnimationFrame(animate);

        return () => {
        document.body.removeChild(stats.dom);
        };
    }, []);

    return null;
};

export default StatsComponent;