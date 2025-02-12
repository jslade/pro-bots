import React, { useContext } from 'react';

import { Grid, Box } from '@mui/material';

import { SessionContext } from '../../contexts/SessionContext';
import { ApiContext } from '../../contexts/ApiContext';

import Scoreboard from './Scoreboard';
import WatcherDisplay from './WatcherDisplay';


import './WatcherLayout.css';

const Workspace = () => {
    const session = useContext(SessionContext);
    const api = useContext(ApiContext);

    return ( <>
        <Grid item xs={12} style={{ height: '1.5em' }}>
            <Box display="flex" flexDirection="column" height="100%">
                <Box flex={1} border={1}>
                    {api ? `Connected [${session.sessionId}]` : 'Disconnected'}
                </Box>
            </Box>
        </Grid>
        <Grid container spacing={0} style={{ height: 'calc(100vh - 1.5em)' }}>
            <Grid item xs={9}>
                <Box display="flex" flexDirection="column" height="100%">
                    <Box flex={1} border={1}>
                        <WatcherDisplay />
                    </Box>
                </Box>
            </Grid>
            <Grid item xs={3}>
                <Box display="flex" flexDirection="column" height="100%">
                    <Box flex={1} border={1}>
                        <Scoreboard />
                    </Box>
                </Box>
            </Grid>
        </Grid>
    </>);
};

export default Workspace;
