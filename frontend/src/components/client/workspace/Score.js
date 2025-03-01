import { useContext, useEffect } from 'react';

import { Grid, Typography } from '@mui/material';

import { GameContext } from '../../../contexts/GameContext';

const Score = () => {
    const { player, scoresUpdated } = useContext(GameContext);

    useEffect(() => {}, [player, scoresUpdated]);
    
    return (
        <Grid container sx={{
            display: 'flex',
            position: 'relative',
            top: '50%',
            transform: 'translateY(-50%)',
        }} spacing={3} >
            <Grid item xs={2}>
                <Typography variant="h6">Score:&nbsp;{player?.score}</Typography>
            </Grid>
        </Grid>
    );
};

export default Score;
