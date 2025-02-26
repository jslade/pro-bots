import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';

import { ApiContext } from './ApiContext';
import { SessionContext } from './SessionContext';
import { ScoreUpdater } from './game/ScoreUpdater';
import { ProbotUpdater } from './game/ProbotUpdater';
import { PlayerUpdater } from './game/PlayerUpdater';
import StatsComponent from '../components/game/Stats';

const GameContext = createContext();

const GameProvider = ({ children }) => {
    const session = useContext(SessionContext);
    const api = useContext(ApiContext);

    const [ gameStateRequested, setGameStateRequested] = useState(false)
    const [ addPlayerRequested, setAddPlayerRequested] = useState(false)

    const [ gameState, setGameState ] = useState(null)
    const [ player, setPlayer ] = useState(null)
    const [ probot, setProbot ] = useState(null)
    const [ pairs, setPairs ] = useState({})

    const [ scoresUpdated, setScoresUpdated ] = useState(null);
    const [ playersUpdated, setPlayersUpdated ] = useState(null);
    const [ probotsUpdated, setProbotsUpdated ] = useState(null);

    const matchPairs = useCallback((players, probots) => {
        const pp = []
        for(const player of players) {
            for(const probot of probots) {
                if (player.name === probot.player) {
                    pp.push({ player, probot });
                }
            }
        }
        console.log("Matched pairs", pp);
        setPairs(pp);
    }, [setPairs])

    const handleGameStateReset = useCallback((data) => {
        setGameState(data.current);
        matchPairs(data.current.players, data.current.probots);
    }, [setGameState, matchPairs])

    const handleGameStateCurrent = useCallback((data) => {
        setGameState(data);
        matchPairs(data.players, data.probots);
    }, [setGameState, matchPairs])

    useEffect(() => {
        if (!api) return;

        api.registerCallback('game', 'reset', (data) => {
            handleGameStateReset(data);
        });
        api.registerCallback('game', 'current_state', (data) => {
            handleGameStateCurrent(data);
        });

    }, [api, api?.registerCallback, handleGameStateCurrent, handleGameStateReset]);

    const requestGameState = useCallback(() => {
        if (!api || gameStateRequested) return;

        console.log("Requesting current game state");
        setGameStateRequested(true);
        api.sendMessage("game", "get_current");
    }, [api, gameStateRequested, setGameStateRequested])

    const requestAddPlayer = useCallback(() => {
        if (!api || !session?.isPlayer || addPlayerRequested) return;

        console.log("Requesting a new Player for me");
        setAddPlayerRequested(true);
        api.sendMessage("game", "add_player", { sessionId: session.sessionId })
    }, [api, addPlayerRequested, setAddPlayerRequested,
        session?.isPlayer, session?.sessionId]);

    useEffect(() => {
        if (!api) {
            setGameStateRequested(false);
            return;
        };

        if (!gameState && !gameStateRequested) {
            requestGameState();
        }

    }, [api, requestGameState, gameStateRequested, gameState]);


    const locatePlayer = useCallback((gameState) => {
        let found = false;
        for(const existing_player of gameState.players) {
            if (existing_player.sessionId === session.sessionId) {
                console.log("Got player for me", existing_player);
                setPlayer(existing_player);
                found = true;

                for(const existing_probot of gameState.probots) {
                    if (existing_probot.player === existing_player.name) {
                        console.log("Got probot for me", existing_probot);
                        setProbot(existing_probot);
                    }
                }
            }
        }
        if (!found) {
            console.log("No player for me");
            setPlayer(null);
            setProbot(null);
        }
        return found;
    }, [
        setPlayer,
        setProbot,
        session.sessionId
    ]);

    useEffect(() => {
        if (!api || !gameState) return;

        console.log("Setting new gameState", gameState);

        if (session.isPlayer) {
            const foundPlayer = locatePlayer(gameState);
            if (!foundPlayer) {
                setAddPlayerRequested(false);
                requestAddPlayer();
            }
        }
    }, [api, gameState,
        locatePlayer,
        requestAddPlayer,
        session?.isPlayer])

    return (
        <GameContext.Provider value={{
            gameState,
            players: gameState?.players || [],
            probots: gameState?.probots || [],
            pairs: pairs || [],
            player, // myself
            probot, // my bot

            scoresUpdated,
        }}>
            <ScoreUpdater
                players={gameState?.players || []}
                setScoresUpdated={setScoresUpdated} />
            <PlayerUpdater
                players={gameState?.players || []}
                setPlayersUpdated={setPlayersUpdated} />
            <ProbotUpdater
                probots={gameState?.probots || []}
                setProbotsUpdated={setProbotsUpdated} />
            {/*<StatsComponent stat={0} />*/}
            {children}
        </GameContext.Provider>
    );
};

export { GameContext, GameProvider };