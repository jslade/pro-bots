import React, { useContext, useEffect, useState } from 'react';

import { Grid, Box } from '@mui/material';

import { SessionContext } from '../../SessionContext';
import { ApiContext } from '../../ApiContext';
import ProgrammingSpace from './ProgrammingSpace';
import CommandSpace from './commands/CommandSpace';
import Display from './Display';
import Controls from './Controls';

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
                    <Box flex={3} border={1}>
                        <ProgrammingSpace />
                    </Box>
                    <Box flex={1} border={0}>
                        <CommandSpace />
                    </Box>
                </Box>
            </Grid>
            <Grid item xs={6}>
                <Box display="flex" flexDirection="column" height="100%">
                    <Box flex={15} border={0}>
                        <Display />
                    </Box>
                    <Box flex={1} border={0}>
                        <Controls />
                    </Box>
                </Box>
            </Grid>
        </Grid>
    </>);
};

export default Workspace;
