import { useContext } from 'react';

import { Grid, Typography } from '@mui/material';

import { GameContext } from '../../../contexts/GameContext';

const Score = () => {
    return (
        <Grid container sx={{
            display: 'flex',
            position: 'relative',
            top: '50%',
            transform: 'translateY(-50%)',
        }} spacing={3} >
            <Grid item xs={2}>
                <Typography variant="h6">Score:&nbsp;<ScoreValue /></Typography>
            </Grid>
        </Grid>
    );
};

const ScoreValue = ({}) => {
    const { player } = useContext(GameContext);

    return (
        <span>{player?.score}</span>
    );
};

export default Score;
