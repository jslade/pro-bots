import React from 'react';
import { Box, Typography } from '@mui/material';
import { PanelGroup, Panel, PanelResizeHandle } from 'react-resizable-panels'

import { SessionContext } from '../../../contexts/SessionContext';
import { ApiContext } from '../../../contexts/ApiContext';

import ProgrammingSpace from './ProgrammingSpace';
import TerminalComponent from './commands/Terminal';
import Overview from '../../game/Overview';
import Display from './Display';
import Controls from './Controls';
import Score from './Score';

import './Layout.css';
import StatsComponent from '../../game/Stats';

const Layout = () => {
    const session = React.useContext(SessionContext);
    const api = React.useContext(ApiContext);

    const promptRef = React.useRef(null);

    const handleClick = React.useCallback(() => {
        promptRef.current?.focus();
    }
    , []);

return (
    <Box sx={{ display: 'flex', width: '100vw', height: '100vh', overflow: "hidden" }}>
        <PanelGroup direction="horizontal" >
            {/* Left Column */}
            <Panel id="left-panel" defaultSize={40} minSize={20}
                    style={{ backgroundColor: 'rgba(102, 153, 255, 0.043)' }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: "hidden" }}>
                    <PanelGroup direction="vertical" id="left-panel-group">
                        <Panel defaultSize={70} minSize={10} id="programming-space"
                            style={{ overflow: "auto", marginBottom: '1px',
                                backgroundColor: 'rgb(40,44,52)'}}
                        >
                            <ProgrammingSpace />
                        </Panel>
                        <PanelResizeHandle />
                        <Panel defaultSize={30} minSize={10} id="terminal"
                            style={{ overflow: "auto", marginTop: '1px',
                                backgroundColor: '#252222' }}
                            onClick={handleClick}
                        >
                            <TerminalComponent promptRef={promptRef} />
                        </Panel>
                    </PanelGroup>
                </Box>
            </Panel>
            <PanelResizeHandle />
            <Panel id="right-panel" defaultSize={60} minSize={30}>
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
                            <Box container style={{ display: 'flex', flexDirection: 'row'}}>
                                <Box sx={{ flex: 1 }}>
                                    <Overview />
                                </Box>
                                <Box sx={{ flex: 1 }}>
                                    <Score />
                                </Box>
                            </Box>
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
