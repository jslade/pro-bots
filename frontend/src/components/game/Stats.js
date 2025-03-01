import React, { useEffect } from 'react';
import Stats from 'stats.js';

const StatsComponent = ({stat=0, container}) => {
    useEffect(() => {
        const stats = new Stats();
        stats.showPanel(stat); // 0: fps, 1: ms, 2: mb, 3+: custom

        const parent = document.querySelector(container) || document.body;
        parent.appendChild(stats.dom);

        parent.firstChild.style.position = 'relative';

        const animate = () => {
            stats.begin();
            stats.end();
            requestAnimationFrame(animate);
        };

        requestAnimationFrame(animate);

        return () => {
            parent.removeChild(stats.dom);
        };
    }, []);

    return null;
};

export default StatsComponent;