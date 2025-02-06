import React, { useContext, useRef } from 'react';
import { useQuery } from '@tanstack/react-query'

import { Container, Box, Button, TextField, Typography } from '@mui/material';

import { SessionContext } from './SessionContext';
import { POST } from '../../api';

const Login = () => {
    const session = useContext(SessionContext);

    const [username, setUsername] = React.useState('');
    const [accessCode, setAccessCode] = React.useState('');
    const [errorMsg, setErrorMsg] = React.useState(null);

    const inputRefs = useRef([]);

    const loginQuery = useQuery({
        queryKey: ['login'],
        queryFn: () => POST(
            `/login`, { username, accessCode }
        ).then(handleResult).catch(handleError),

        refetchOnWindowFocus: false,
        enabled: false,
        retry: false,
    });

    const handleSubmit = () => {
        loginQuery.refetch();
    }

    const handleResult = (data) => {
        if (data?.sessionId) {
            session.setSessionId(data.sessionId);
            session.setName(username);
        }

        return data;
    }

    const handleError = (error) => {
        if (error.response.status === 401) {
            const data = error.response.data;
            setErrorMsg(data.message || "Something went wrong");
        } else {
            setErrorMsg(`Something went wrong: ${error.message}`);
        }
    }

    return (
        <Container
            sx={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh',
            }}
        >
            <Typography variant="h4" gutterBottom>
                Welcome
            </Typography>

            <Box>
                <Typography variant="body1" align="center" gutterBottom>
                    Enter your username and access code to login.<br />
                    If you haven't created a user before, it will be created automatically
                </Typography>
            </Box>

            <Box
                component="form"
                autoComplete="off"
                sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 2,
                    width: '300px',
                }}
            >
                <TextField label="Username" variant="outlined" fullWidth 
                    autoFocus={true}
                    onChange={e => setUsername(e.target.value)}
                    onKeyDown={(e) => (
                        e.key === 'Enter' ? inputRefs.current[1].focus() : null
                        )}
                />
                <TextField label="Access Code" variant="outlined" fullWidth
                    inputRef={(ref) => (inputRefs.current[1] = ref)}
                    onChange={e => setAccessCode(e.target.value)}
                    onKeyDown={(e) => (
                        e.key === 'Enter' ? handleSubmit() : null
                    )}
                />
                <Button 
                    variant="contained" 
                    color="primary" 
                    fullWidth 
                    onClick={handleSubmit}
                >
                    Login
                </Button>
            </Box>

            {errorMsg ? <Box>
                <Typography variant="body1" align="center" gutterBottom>
                    Login failed: {errorMsg}
                </Typography>
            </Box> : null}
        </Container>
    );
};

export default Login;