import React from 'react';
import { Box, Grid, TextField } from '@mui/material';
import { ApiProvider, ApiContext } from '../../contexts/ApiContext';

import ProgrammingSpace from './workspace/ProgrammingSpace';
import { SessionContext } from '../../contexts/SessionContext';
import Login from './Login';

const CodeViewer = () => {
    const session = React.useContext(SessionContext);

    return (
        <ApiProvider>
            {session.sessionId ? <CodeViewerLayout /> : <Login />}
        </ApiProvider>
    );
};

const CodeViewerLayout = () => {
    const session = React.useContext(SessionContext);
    const api = React.useContext(ApiContext);

    const [profile, setProfile] = React.useState(null);
    const textRef = React.useRef(null);

    React.useEffect(() => {
        if (!api) return;
        api.setIgnoreUnknown(true);
    }, [api]);
    
    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            const p = textRef.current.value;
            setProfile(p);
        }
    };

    return (
        <div>
            <Grid container sx={{ display: 'flex', flexDirection: 'column' }}>
                <Box item xs={1} p={1}>
                    {session.sessionId ? `Connected: ${session.sessionId}` : 'Disconnected'}
                </Box>
                <Box item xs={1} p={1}>
                    <TextField label="Profile" inputRef={textRef}
                        onKeyDown={(e) => {handleKeyPress(e)}} />
                </Box>
                <Grid item xs={12}>
                    <ProgrammingSpace readOnly={true} profile={profile} />
                </Grid>
            </Grid>
        </div> )
};

export default CodeViewer;