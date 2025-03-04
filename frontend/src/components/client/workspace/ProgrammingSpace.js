import React from 'react';
import ReactCodeMirror from '@uiw/react-codemirror';
import { langs } from '@uiw/codemirror-extensions-langs';
import { Grid, Button, Box, Typography } from '@mui/material';

import { ApiContext } from '../../../contexts/ApiContext';

import './ProgrammingSpace.css';

const ProgrammingSpace = ({ readOnly = false, profile = null }) => {
    const api = React.useContext(ApiContext);

    const [program, setProgram] = React.useState(null);

    React.useEffect(() => {
        if (!api) return;

        api.registerCallback('user', 'get_program', (data) => {
            setProgram(data.program);
        });

        return () => {
            api?.unregisterCallback('user', 'get_program');
        }
    }, [api, program, setProgram]);

    React.useEffect(() => {
        if (!api) return;

        api.sendMessage('user', 'get_program', { profile });
    }, [api, profile]);

    const handleCodeChange = React.useCallback((value, viewUpdate) => {
        setProgram(value);
    }, [setProgram]);

    const handleHelp = React.useCallback((event) => {
        const helpUrl = "https://github.com/jslade/pro-bots/wiki/Probotics";
        window.open(helpUrl, '_blank').focus();
    }, []);
    const handleSave = React.useCallback((event) => {
        if (readOnly) return;
        api.sendMessage('user', 'update_program', { program: program });
    }, [api, program, readOnly]);
    const handleSaveAndRun = React.useCallback((event) => {
        if (readOnly) return; 
        api.sendMessage('user', 'update_program', { program: program, run: true });
    }, [api, program, readOnly]);
    const handleStop = React.useCallback((event) => {
        if (readOnly) return;
        api.sendMessage('user', 'stop_program', { program: program, run: true });
    }, [api, program, readOnly]);

    const controls = ()  => {
        return (
            <Grid container sx={{
                display: 'box',
                justifyContent: 'left',
                alignItems: 'center',
                backgroundColor: '#d0d0d0',
                position: 'fixed',
                top: '0',
                left: '0',
                zIndex: '1',
            }} spacing={1} >
                <Grid item xs={1}>
                    <Button onClick={handleHelp}>Help</Button>
                </Grid>
                <Grid item xs={1}>
                    <Button onClick={handleSave}>Save</Button>
                </Grid>
                <Grid item xs={1}>
                    <Button variant="contained" onClick={handleSaveAndRun}>Run</Button>
                </Grid>
                <Grid item xs={2}>
                    <Button onClick={handleStop}>Stop</Button>
                </Grid>
            </Grid>
        );
    }

    return ( <>
        {readOnly ? null : controls()}
        <Grid container sx={{display: 'flex', flexDirection: 'column', overflow: 'auto',
                    backgroundColor: 'rgba(102, 153, 255, 0.043)', position: 'relative'
                }}>
            <Grid item sx={{ paddingTop: readOnly ? 0 : '2.5rem' }}>
                <ReactCodeMirror
                    className="editor"
                    value={program || ''}
                    theme="dark"
                    extensions={[langs.go()]}
                    onChange={handleCodeChange}
                    style={{ height: '100%' }}
                />
            </Grid>
        </Grid>

        </>
    );
};

export default ProgrammingSpace;