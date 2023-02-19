import React, {useState} from 'react';
import './App.css';
import Card, {CardState} from "./Card";
import {Box, Container, Stack} from "@mui/material";
import wordPairsJSON from "./wordPairs.json";

function choice<T>(arr: Array<T>): T {
  // if (!arr.length || arr.length === 0) return;
  return arr[Math.floor(Math.random() * arr.length)];
}

function shuffle<T>(arr: Array<T>): Array<T> {
  return arr.sort(() => Math.random() - 0.5);
}

function chunks<T>(arr: Array<T>, size: number): Array<Array<T>> {
  const result = [];
  for (let i = 0; i < arr.length; i += size) {
    result.push(arr.slice(i, i + size));
  }
  return result;
}

function intersection<T>(a: Array<T>, b: Array<T>): Array<T> {
  return a.filter((x) => b.includes(x));
}

const speak = (word: string) => {
  const voices = speechSynthesis.getVoices();
  const voice = voices.find((v) => v.name === 'Google US English');
  const utterance = new SpeechSynthesisUtterance(word);
  utterance.voice = voice || null;
  utterance.pitch = 1.0; // + Math.random() * 0.2;
  utterance.rate = 1.0; //0.7 + Math.random() * 0.3;
  utterance.lang = 'en-US'
  speechSynthesis.speak(utterance);
};

function weightedRandomSample<T>(arr: Array<T>, weights: Array<number>, sampleSize: number): Array<T> {
  let remainingItems = [...arr];
  let remainingWeights = [...weights];
  const result = [];
  for (let i = 0; i < sampleSize; i++) {
    const cumulativeWeights = remainingWeights.reduce((acc, w) => [...acc, w + (acc.length > 0 ? acc[acc.length - 1] : 0)], [] as Array<number>);
    const r = Math.random() * cumulativeWeights[cumulativeWeights.length - 1];
    const index = cumulativeWeights.findIndex((w) => w > r);
    result.push(remainingItems[index]);
    remainingItems.splice(index, 1);
    remainingWeights.splice(index, 1);
  }
  return result;
}

const generateCards = (gridWidth: number, gridHeight: number): Array<CardState> => {
    const wordsPairs = wordPairsJSON as Array<{
      weight: number,
      word: string,
      pictures: string[],
      audio?: string[],
      color?: string,
      glyph?: string,
    }>
    const gridSize = gridWidth * gridHeight;
    // todo: smarter way to select words, exclude banned word / category / picture combinations
    const selectedWordsPairs = weightedRandomSample(wordsPairs, wordsPairs.map(wp => wp.weight), Math.floor(gridSize / 2));  // 8 words
    const cardDefs = selectedWordsPairs.map((pair, i) => {
      const word = pair.word;
      const picture = choice(pair.pictures);
      return [
        {id: `word-${i}`, word: word, picture: undefined, src: pair},
        {id: `pic-${i}`, picture: picture, color: pair.color, glyph: pair.glyph, src: pair, word: word, audio: pair.audio},
      ]
    });
    const cardsArray: Array<CardState> = shuffle(cardDefs[0].concat(...cardDefs.slice(1)).map((card, i) => (
      {
        ...card,
      }
    )));
    return cardsArray;
  }

function App() {

  const gridWidth = 4;
  const gridHeight = 4;

  const [cards, setCards] = useState(generateCards(gridWidth, gridHeight));
  const [selected, setSelected] = useState<CardState | undefined>(undefined);

  const onCardsMatched = (card1: CardState, card2: CardState) => {
    // match
    // play sound effect
    // fade out cards from the board
    speak(choice(["Awesome!", "Great!", "Good job!", "Nice!", "Perfect!", "Super!", "Well done!"]));
    setSelected(undefined)
    card1.hidden = true
    card1.selected = false

    card2.hidden = true
    card2.selected = false
    if (cards.filter(c => !c.hidden).length === 0) {
      onAllCardsHidden()
    } else {
      setCards([...cards])
    }

  }
  const onCardsMismatched = (card: CardState, selected: CardState) => {
    // no match
    // add .shake class for 1 second
    // remove .shake class
    if(card.word) {
      speak(card.word)
    }
    speak(choice(["No!", 'Nope!', 'Try again!', 'Wrong!']));
    setSelected(undefined)
    setCards(cards.map((c) => {
      if (c.id === selected.id || c.id === card.id) {
        return {...c, selected: false, shake: true}
      }
      return c
    }))
    setTimeout(() => {
      setCards(cards.map((c) => {
        if (c.id === selected.id || c.id === card.id) {
          return {...c, selected: false, shake: false}
        }
        return c
      }))
    }, 1000)
  }
  const selectCard = (card: CardState) => {
    setSelected(card);
    card.selected = true;
    if (card.word) {
      speak(card.word)
    }
    setCards([...cards]);
  }
  const deselectCard = (card: CardState) => {
    card.selected = false;
    setSelected(undefined);
    setCards([...cards]);
  }
  const onClickCard = (card: CardState) => {
    if(card.hidden) return;
    if (selected === undefined) {
      selectCard(card);
    } else if (card.id === selected.id) {
      deselectCard(card);
    } else if (selected.src.word === card.src.word) {
      onCardsMatched(card, selected);
    } else {
      onCardsMismatched(card, selected);
    }
  }

  const onAllCardsHidden = () => {
    speak("You win!");
    setTimeout(() => {
      setCards(generateCards(gridWidth, gridHeight))
    }, 1000)
  }
  return (
    <div className="App">
      <Box sx={{
          mt: {
            xs: 1,
            sm: 3,
            md: 6,
            lg: 10
          },
          padding: 0,
          maxWidth: {
            xs: '100%',
            sm: '440px',
            md: '660px',
            lg: '880px',
          },
          display: 'inline-block',
        }}
      >
        <Stack
          spacing={{
            xs: 0,
            sm: 1,
            lg: 2
          }}>
        {
          chunks(cards, 4).map((row, i) => (
            <Stack key={`row-${i}`} direction='row' spacing={{
              xs: 0,
              sm: 1,
              lg: 2
            }}>
              {
                row.map((card) => (
                  <Box
                    sx={{
                      width: {
                        xs: '100px',
                        sm: '100px',
                        md: '150px',
                        lg: '200px',
                      },
                      height: {
                        xs: '100px',
                        sm: '100px',
                        md: '150px',
                        lg: '200px',
                      },
                      display: 'inline-block',
                    }}
                    key={card.id}
                  >
                    <Card
                      card={card}
                      key={card.id}
                      className={`${card.selected ? 'selected' : ''} ${card.hidden ? 'hidden' : ''} ${card.shake ? 'shake' : ''} ${card.src.props?.className || ''}`}
                      style={card.src.props?.css||{}}
                      onClick={() => onClickCard(card)}
                    />
                  </Box>
                ))
              }
            </Stack>
          ))
        }
        </Stack>
      </Box>
    </div>
  );
}

export default App;
