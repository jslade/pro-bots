import React from 'react';
import ReactCodeMirror from '@uiw/react-codemirror';
import { langs } from '@uiw/codemirror-extensions-langs';
import { Grid, Button, Box, Typography } from '@mui/material';

import { ApiContext } from '../../../contexts/ApiContext';

import './ProgrammingSpace.css';

const ProgrammingSpace = ({}) => {
    const api = React.useContext(ApiContext);

    const [program, setProgram] = React.useState('');

    React.useEffect(() => {
        if (!api) return;

        if (program === '') {
            api.registerCallback('user', 'get_program', (data) => {
                setProgram(data.program);
            });
            api.registerCallback('user', 'update_program', (data) => {
                console.log("Program updated:", data);
            });

            api.sendMessage('user', 'get_program', {});
        }
    }, [api, program, setProgram]);

    const handleCodeChange = React.useCallback((value, viewUpdate) => {
        setProgram(value);
    }, [setProgram]);

    const handleSave = React.useCallback((event) => {
        api.sendMessage('user', 'update_program', { program: program });
    }, [api, program]);
    const handleSaveAndRun = React.useCallback((event) => {
        api.sendMessage('user', 'update_program', { program: program, run: true });
    }, [api, program]);
    const handleStop = React.useCallback((event) => {
        api.sendMessage('user', 'stop_program', { program: program, run: true });
    }, [api, program]);

    return ( <>
        <Grid container sx={{display: 'flex', flexDirection: 'column', overflow: 'auto'}}>
            <Grid item sx={{ flex: 1, overflow: 'hidden' }}>
                <ReactCodeMirror
                    className="editor"
                    value={program}
                    theme="dark"
                    extensions={[langs.go()]}
                    onChange={handleCodeChange}
                    style={{ height: '100%' }}
                />
            </Grid>
            <Grid item xs={1} >
                <Box sx={{ flexDirection: 'row', display: "flex" }} border={0}>
                    <Button onClick={handleSave}>Save</Button>
                    <Button onClick={handleSaveAndRun}>Run</Button>
                    <Button onClick={handleStop}>Stop</Button>
                </Box>
            </Grid>
        </Grid>
        </>
    );
};

export default ProgrammingSpace;