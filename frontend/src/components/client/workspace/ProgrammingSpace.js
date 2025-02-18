import React from 'react';
import ReactCodeMirror from '@uiw/react-codemirror';
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

    return ( <>
    <Grid container spacing={0} style={{ height: '100%' }}>

        <Box flex={30} border={1} borderColor="hotpink">
            <ReactCodeMirror
                className="editor"
                value={program}
                height="100%"
                extensions={[/* Add your desired extensions here */]}
                theme="dark"
                onChange={handleCodeChange}
            />
        </Box>
        <Box flex={1} className="controls" border={1} borderColor="green">
            <Button onClick={handleSave}>Save</Button>
            <Button onClick={handleSaveAndRun}>Run</Button>
        </Box>
    </Grid>
        </>
    );
};

export default ProgrammingSpace;