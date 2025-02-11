import React from 'react';

import { ApiProvider } from '../../../contexts/ApiContext';
import { GameProvider } from '../../../contexts/GameContext';

import Layout from './Layout';

const Workspace = () => {

    return (
        <ApiProvider>
            <GameProvider>
                <Layout />
            </GameProvider>
        </ApiProvider>
    );
};

export default Workspace;
