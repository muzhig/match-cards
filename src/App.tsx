import React, {useState} from 'react';
import './App.css';
import Card, {CardState} from "./Card";
import {Box, Container} from "@mui/material";

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
    console.log(i, remainingItems, remainingWeights);
    const cumulativeWeights = remainingWeights.reduce((acc, w) => [...acc, w + (acc.length > 0 ? acc[acc.length - 1] : 0)], [] as Array<number>);
    const r = Math.random() * cumulativeWeights[cumulativeWeights.length - 1];
    const index = cumulativeWeights.findIndex((w) => w > r);
    result.push(remainingItems[index]);
    remainingItems.splice(index, 1);
    remainingWeights.splice(index, 1);
  }
  console.log(result);
  return result;
}

function App() {
  const wordsPairs = [
    {words: ['car'], pictures: ['car-1.png', 'car-2.png', 'car-3.png', 'car-4.png'], categories: ['toys', 'vehicles'], weight: 1},
    {words: ['ruler'], pictures: ['ruler-1.png', 'ruler-2.png'], categories: ['school'], weight: 1},
    {words: ['pencil'], pictures: ['pencil.png', 'pencil-2.png', 'pencil-3.png', 'pencil-4.png', 'pencil-5.png', 'pencil-6.png', 'pencil-7.png'], categories: ['school'], weight: 1},
    {words: ['eraser', 'rubber'], pictures: ['eraser.png', 'eraser-2.png', 'eraser-3.png'], categories: ['school'], weight: 1},
    {words: ['rocket'], pictures: ['rocket.png', 'rocket-2.png', 'rocket-3.png', 'rocket-4.png'], categories: ['toys', 'vehicles'], weight: 1},

    {words: ['cat'], pictures: ['cat.png', 'cat-2.png', 'cat-3.png', 'cat-4.png'], categories: ['animals'], weight: 1},
    {words: ['dog'], pictures: ['dog.png', 'dog-2.png', 'dog-3.png', 'dog-4.png', 'dog-5.png', 'dog-6.png', 'dog-7.png', 'dog-8.png'], categories: ['animals'], weight: 1},
    {words: ['ball'], pictures: ['ball.png', 'ball-2.png', 'ball-3.png', 'ball-4.png'], categories: ['toys'], weight: 1},
    {words: ['tree'], pictures: ['tree.png'], categories: ['nature'], weight: 1},
    {words: ['toys'], pictures: ['toys.png', 'toys-2.png', 'toys-3.png', 'toys-4.png'], categories: ['toys'], weight: 1},
    {words: ['book'], pictures: ['book.png', 'book-2.png', 'book-3.png', 'book-4.png', 'book-5.png'], categories: ['school'], weight: 1},
    {words: ['apple'], pictures: ['apple-1672572113.png'], categories: ['food'], weight: 1},
    {words: ['banana'], pictures: ['banana-1672572189.png', 'banana-1672572223.png'], categories: ['food'], weight: 1},
    {words: ['bread'], pictures: ['bread-1672571934.png'], categories: ['food'], weight: 1},
    {words: ['chair'], pictures: ['chair.png', 'chair-2.png'], categories: ['school', 'furniture'], weight: 1},
    {words: ['chicken'], pictures: ['chicken-1672572083.png', 'chicken-1672572060.png'], categories: ['food', 'animals'], weight: 1},
    {words: ['elephant'], pictures: ['elephant.png', 'elephant-2.png'], categories: ['animals'], weight: 1},
    {words: ['fish'], pictures: ['fish-1672641718.png', 'fish-2.png', 'fish-3.png', 'fish-4.png', 'fish-5.png'], categories: ['animals'], weight: 1},
    {words: ['meat'], pictures: ['meat.png', 'meat-1672572304.png'], categories: ['food'], weight: 1},
    {words: ['milk'], pictures: ['milk-1.png', 'milk-2.png', 'milk-3.png'], categories: ['food'], weight: 1},
    {words: ['pizza'], pictures: ['pizza.png', 'pizza-2.png'], categories: ['food'], weight: 1},
    {words: ['potato'], pictures: ['potato.png', 'potato-2.png', 'potato-1672572315.png'], categories: ['food'], weight: 1},
    {words: ['flower'], pictures: ['flower-1.png', 'flower-2.png', 'flower-3.png', 'flower-4.png', 'flower-5.png',
        'flower-7.png', 'flower-8.png', 'flower-9.png', 'flower-10.png', 'flower-11.png', 'flower-12.png',
        'flower-13.png', 'flower-14.png', 'flower-15.png'], categories: ['nature'], weight: 1},
    {words: ['yellow'], pictures: [], color: '#ffcc00', categories: ['colors'], weight: 0.2},
    {words: ['red'], pictures: [], color: '#cc3300', categories: ['colors'], weight: 0.2},
    {words: ['blue'], pictures: [], color: '#00ccff', categories: ['colors'], weight: 0.2},
    {words: ['green'], pictures: [], color: '#006600', categories: ['colors'], weight: 0.2},
    {words: ['orange'], pictures: [], color: '#ff6600', categories: ['colors'], weight: 0.2},
    // {words: ['white'], pictures: [], color: 'white', categories: ['colors'], weight: 0.2},
    {words: ['black'], pictures: [], color: '#262626', categories: ['colors'], weight: 0.2},
    {words: ['purple'], pictures: [], color: '#660066', categories: ['colors'], weight: 0.2},
    {words: ['brown'], pictures: [], color: '#4d2600', categories: ['colors'], weight: 0.2},
    {words: ['pink'], pictures: [], color: '#ffccff', categories: ['colors'], weight: 0.2},
    {words: ['gray'], pictures: [], color: '#808080', categories: ['colors'], weight: 0.2},

    {words: ['zero'], pictures: [], glyph: '0', categories: ['numbers'], weight: 0.1},
    {words: ['one'], pictures: [], glyph: '1', categories: ['numbers'], weight: 0.1},
    {words: ['two'], pictures: [], glyph: '2', categories: ['numbers'], weight: 0.1},
    {words: ['three'], pictures: [], glyph: '3', categories: ['numbers'], weight: 0.1},
    {words: ['four'], pictures: [], glyph: '4', categories: ['numbers'], weight: 0.1},
    {words: ['five'], pictures: [], glyph: '5', categories: ['numbers'], weight: 0.1},
    {words: ['six'], pictures: [], glyph: '6', categories: ['numbers'], weight: 0.1},
    {words: ['seven'], pictures: [], glyph: '7', categories: ['numbers'], weight: 0.1},
    {words: ['eight'], pictures: [], glyph: '8', categories: ['numbers'], weight: 0.1},
    {words: ['nine'], pictures: [], glyph: '9', categories: ['numbers'], weight: 0.1},

    {words: ['smile'], pictures: [], glyph: '😀', categories: ['emotions'], weight: 1},
    {words: ['heart', 'love'], pictures: [], glyph: '❤️', categories: ['emotions'], weight: 1},
    {words: ['drum'], pictures: [], glyph: '🥁', categories: ['emotions', 'toys'], weight: 1},
    {words: ['fire'], pictures: [], glyph: '🔥', categories: ['emotions', 'toys'], weight: 1},
    {words: ['like'], pictures: [], glyph: '👍', categories: ['emotions',], weight: 1},
    {words: ['finger'], pictures: [], glyph: '☝️', categories: ['emotions'], weight: 1},
    {words: ['star'], pictures: [], glyph: '⭐️', categories: ['emotions'], weight: 1},
  ]
  const gridWidth = 4;
  const gridHeight = 4;
  const gridSize = gridWidth * gridHeight;
  const selectedWordsPairs = weightedRandomSample(wordsPairs, wordsPairs.map(wp => wp.weight), Math.floor(gridSize / 2));  // 8 words
  const cardDefs = selectedWordsPairs.map((pair, i) => [
    {id: `word-${i}`, word: choice(pair.words), picture: undefined, src: pair},
    {id: `pic-${i}`, picture: choice(pair.pictures), color: pair.color, glyph: pair.glyph, src: pair},
  ]);
  const cardsArray: Array<CardState> = shuffle(cardDefs[0].concat(...cardDefs.slice(1)).map((card, i) => (
    {
      ...card,
    }
  )));
  // shuffled
  const [cards, setCards] = useState(cardsArray);
  const [selected, setSelected] = useState<CardState | undefined>(undefined);


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
          maxWidth: 440,
          display: 'inline-block',
        }}
      >
        {chunks(cards, gridWidth).map((row) => (
          <>
            {
              row.map((card, i) => (
              // <Box sx={{spacing: {xs: 0, sm: 1}}} key={i}>
              <Card
                card={card}
                key={card.id}
                className={`${card.selected ? 'selected' : ''} ${card.hidden ? 'hidden' : ''} ${card.shake ? 'shake' : ''} ${card.src.props?.className || ''}`}
                style={card.src.props?.css||{}}
                onClick={() => {
                  if(card.hidden) return;
                  if (selected && selected.id !== card.id) {
                    if (intersection(selected.src.words, card.src.words).length > 0) {
                      // match
                      // play sound effect
                      // fade out cards from the board
                      speak(choice(["Awesome!", "Great!", "Good job!", "Nice!", "Perfect!", "Super!", "Well done!"]));
                      setSelected(undefined)
                      setCards(cards.map((c) => {
                        if (c.id === selected.id || c.id === card.id) {
                          return {...c, selected: false, hidden: true}
                        }
                        return c
                      }))
                    } else {
                      if(card.word) {
                        speak(card.word)
                      }
                      // no match
                      // add .shake class for 1 second
                      // remove .shake class
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
                  } else {
                    if (card.selected) {
                      card.selected =  false
                      setSelected(undefined)
                    } else {
                      card.selected =  card.selected? false : true
                      setSelected(card)
                      if (card.selected && card.word) {
                        speak(card.word)
                      }
                    }
                    setCards([...cards])
                  }
                }}
              />
              // </Box>
            ))
            }
            {/*<br/>*/}
          </>
        ))
        }
      </Box>
    </div>
  );
}

export default App;
