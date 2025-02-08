import React, { useContext } from 'react';

import { Grid, Box } from '@mui/material';

import { SessionContext } from '../../SessionContext';
import ProgrammingSpace from './ProgrammingSpace';
import CommandSpace from './commands/CommandSpace';
import HUD from './HUD';

const Workspace = () => {
    const session = useContext(SessionContext);
    
    return ( <>
        <Grid item xs={12} style={{ height: '1.5em' }}>
            <Box display="flex" flexDirection="column" height="100%">
                <Box flex={1} border={1}>
                    {session.connected ? 'Connected' : 'Disconnected'}
                </Box>
            </Box>
        </Grid>
        <Grid container spacing={2} style={{ height: 'calc(100vh - 1.5em)' }}>
            <Grid item xs={6}>
                <Box display="flex" flexDirection="column" height="100%">
                    <Box flex={1} border={1}>
                        <ProgrammingSpace />
                    </Box>
                    <Box flex={1} border={1}>
                        <CommandSpace />
                    </Box>
                </Box>
            </Grid>
            <Grid item xs={6}>
                <Box height="100%" border={1}>
                    <HUD />
                </Box>
            </Grid>
        </Grid>
    </>);
};

export default Workspace;
