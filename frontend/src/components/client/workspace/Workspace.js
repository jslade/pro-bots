import React from 'react';
import { Grid, Box } from '@mui/material';
import ProgrammingSpace from './ProgrammingSpace';
import CommandSpace from './CommandSpace';
import HUD from './HUD';

const Workspace = () => {
    return (
        <Grid container spacing={2} style={{ height: '100vh' }}>
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
    );
};

export default Workspace;
