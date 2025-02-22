import React, { useContext } from 'react';
import { Grid, Box } from '@mui/material';

import { SessionContext } from '../../../contexts/SessionContext';
import { ApiContext } from '../../../contexts/ApiContext';

import ProgrammingSpace from './ProgrammingSpace';
import CommandSpace from './commands/CommandSpace';
import Overview from '../../game/Overview';
import Display from './Display';
import Controls from './Controls';

import './Layout.css';

const Layout = () => {
    const session = useContext(SessionContext);
    const api = useContext(ApiContext);

return ( <div maxheight="100vh" style={{ display: 'block', height: '100vh' }}>
        <Grid item xs={12} style={{ height: '1.5em' }}>
            <Box display="flex" flexDirection="column" height="100%">
                <Box flex={1} border={1}>
                    {api ? `Connected [${session.sessionId}]` : 'Disconnected'}
                </Box>
            </Box>
        </Grid>
        <Grid container spacing={0} style={{ height: 'calc(100vh - 1.5em)', maxheight: 'calc(100vh - 1.5em)' }}> 
            <Grid item xs={6}>
                <Box display="flex" flexDirection="column" height="100%">
                    <Box flex={3} border={0} borderColor="blue">
                        <ProgrammingSpace />
                    </Box>
                    <Box flex={1} border={0} borderColor="white">
                        <CommandSpace />
                    </Box>
                </Box>
            </Grid>
            <Grid item xs={6}>
                <Box display="flex" flexDirection="column" height="100%">
                    <Box flex={4} border={1}>
                        <Overview />
                    </Box>
                    <Box flex={12} border={0}>
                        <Display />
                    </Box>
                    <Box flex={1} border={0}>
                        <Controls />
                    </Box>
                </Box>
            </Grid>
        </Grid>
    </div>);
};

export default Layout;
