import React, { useContext } from 'react';
import { useQuery } from '@tanstack/react-query'

import { Container, Box, Button, TextField, Typography } from '@mui/material';

import { ApiContext } from '../ApiContext';

const Login = () => {
    const api = useContext(ApiContext);
    const [username, setUsername] = React.useState('');
    const [accessCode, setAccessCode] = React.useState('');

    const { isFetching, data: login_result, refetch } = useQuery({
        queryKey: ['login'],
        queryFn: () => api.POST(
            { path: `/login`, body: { username, accessCode } }
        ).then((data) => handleResult(data)),
        refetchOnWindowFocus: false,
        enabled: false
    });

    const handleSubmit = () => {
        refetch();
    }

    const handleResult = (data) => {
        console.log(data);
        return data;
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
                sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 2,
                    width: '300px',
                }}
            >
                <form autocomplete="off">
                    <TextField label="Username" variant="outlined" fullWidth 
                        onChange={e => setUsername(e.target.value)}/>
                    <TextField label="Access Code" variant="outlined" fullWidth
                        onChange={e => setAccessCode(e.target.value)}/>
                </form>
                <Button 
                    variant="contained" 
                    color="primary" 
                    fullWidth 
                    onClick={handleSubmit}
                >
                    Login
                </Button>
            </Box>
        </Container>
    );
};

export default Login;