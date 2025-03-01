import React from 'react';
import { Box, Button, Typography } from '@mui/material';
import { PanelGroup, Panel, PanelResizeHandle } from 'react-resizable-panels'

import { SessionContext } from '../../../contexts/SessionContext';
import { ApiContext } from '../../../contexts/ApiContext';

import ProgrammingSpace from './ProgrammingSpace';
import CommandSpace from './commands/CommandSpace';
import Overview from '../../game/Overview';
import Display from './Display';
import Controls from './Controls';

import './Layout.css';
import StatsComponent from '../../game/Stats';

const OverviewScene = () => {
    return null
};
const MainScene = () => {
    return null
};

const Layout = () => {
    const session = React.useContext(SessionContext);
    const api = React.useContext(ApiContext);

return (
    <Box sx={{ display: 'flex', width: '100vw', height: '100vh', overflow: "hidden" }}>
        <PanelGroup direction="horizontal" >
            {/* Left Column */}
            <Panel defaultSize={30} minSize={10}>
                <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: "hidden" }}>
                    <PanelGroup direction="vertical">
                        <Panel defaultSize={70} minSize={10}>
                            <div style={{ overflow: "auto" }} >
                                <ProgrammingSpace />
                            </div>
                        </Panel>
                        <PanelResizeHandle />
                        <Panel defaultSize={30} minSize={10}>
                            <div style={{ overflow: "auto" }} >
                                <CommandSpace />
                            </div>
                        </Panel>
                    </PanelGroup>
                </Box>
            </Panel>
            <PanelResizeHandle />
            <Panel defaultSize={70} minSize={10}>
                {/* Right Column */}
                <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: "hidden" }}>
                    {/* Status Field */}
                    <Box sx={{ backgroundColor: '#d0d0d0', p: 1 }}>
                        <Typography variant="body1">{api ? `Connected [${session.sessionId}]` : 'Disconnected'}
                        </Typography>
                        <div id="stats0" style={{position: 'fixed', top: 0, right: 0}} />
                        <StatsComponent container="#stats0"/>
                    </Box>
                    {/* Overview and Main Scene */}
                    <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
                        <Box sx={{ flex: 1 }}>
                            <Overview />
                        </Box>
                        <Box sx={{ flex: 5 }}>
                            <Display />
                        </Box>
                    </Box>
                    <Controls />
                </Box>
            </Panel>
        </PanelGroup>
    </Box>
    );
};

export default Layout;
