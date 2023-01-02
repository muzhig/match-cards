import React, {useState} from 'react';
import './App.css';
import Card, {CardState} from "./Card";

/*
// A game where player can learn english words by matching cards
// Prototype, a board with a grid of cards 10 x 10
// A card is a word or a picture
// A card can clicked to select it, and then another card can be clicked to match it
// If the cards match, they are removed from the board and an SFX is played.

*/

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
    utterance.pitch = 1.0 + Math.random() * 0.2;
    utterance.rate = 0.7 + Math.random() * 0.3;
    utterance.lang = 'en-US'

    speechSynthesis.speak(utterance);
  };

function App() {
  const wordsPairs = [
    {words: ['car'], pictures: ['car-1.png', 'car-2.png', 'car-3.png', 'car-4.png']},
    {words: ['ruler'], pictures: ['ruler-1.png', 'ruler-2.png']},
    {words: ['pencil'], pictures: ['pencil.png', 'pencil-2.png', 'pencil-3.png', 'pencil-4.png', 'pencil-5.png', 'pencil-6.png', 'pencil-7.png']},
    {words: ['eraser', 'rubber'], pictures: ['eraser.png', 'eraser-2.png', 'eraser-3.png']},
    {words: ['rocket'], pictures: ['rocket.png', 'rocket-2.png', 'rocket-3.png', 'rocket-4.png']},

    {words: ['cat'], pictures: ['cat.png', 'cat-2.png', 'cat-3.png', 'cat-4.png']},
    {words: ['dog'], pictures: ['dog.png', 'dog-2.png', 'dog-3.png', 'dog-4.png', 'dog-5.png', 'dog-6.png', 'dog-7.png', 'dog-8.png']},
    {words: ['ball'], pictures: ['ball.png', 'ball-2.png', 'ball-3.png', 'ball-4.png']},
    {words: ['tree'], pictures: ['tree.png']},
    {words: ['toys'], pictures: ['toys.png', 'toys-2.png', 'toys-3.png', 'toys-4.png']},
    {words: ['book'], pictures: ['book.png', 'book-2.png', 'book-3.png', 'book-4.png', 'book-5.png']},
    {words: ['apple'], pictures: ['apple-1672572113.png']},
    {words: ['banana'], pictures: ['banana-1672572189.png', 'banana-1672572223.png']},
    {words: ['bread'], pictures: ['bread-1672571934.png']},
    {words: ['chair'], pictures: ['chair.png', 'chair-2.png']},
    {words: ['chicken'], pictures: ['chicken-1672572083.png', 'chicken-1672572060.png']},
    {words: ['elephant'], pictures: ['elephant.png', 'elephant-2.png']},
    {words: ['fish'], pictures: ['fish-1672641718.png', 'fish-2.png', 'fish-3.png', 'fish-4.png', 'fish-5.png']},
    {words: ['meat'], pictures: ['meat.png', 'meat-1672572304.png']},
    {words: ['milk'], pictures: ['milk-1.png', 'milk-2.png', 'milk-3.png']},
    {words: ['pizza'], pictures: ['pizza.png', 'pizza-2.png']},
    {words: ['potato'], pictures: ['potato.png', 'potato-2.png', 'potato-1672572315.png']},
    {words: ['flower'], pictures: ['flower-1.png', 'flower-2.png', 'flower-3.png', 'flower-4.png', 'flower-5.png',
        'flower-7.png', 'flower-8.png', 'flower-9.png', 'flower-10.png', 'flower-11.png', 'flower-12.png',
        'flower-13.png', 'flower-14.png', 'flower-15.png']},
    {words: ['yellow'], pictures: [], color: 'yellow'},
    {words: ['red'], pictures: [], color: 'red'},
    {words: ['blue'], pictures: [], color: 'blue'},
    {words: ['green'], pictures: [], color: 'green'},
    {words: ['orange'], pictures: [], color: 'orange'},
    // {words: ['white'], pictures: [], color: 'white'},
    {words: ['black'], pictures: [], color: 'black'},
    {words: ['purple'], pictures: [], color: 'purple'},
    {words: ['brown'], pictures: [], color: 'brown'},
    {words: ['pink'], pictures: [], color: 'pink'},
    {words: ['gray'], pictures: [], color: 'gray'},

    {words: ['zero'], pictures: [], glyph: '0'},
    {words: ['one'], pictures: [], glyph: '1'},
    {words: ['two'], pictures: [], glyph: '2'},
    {words: ['three'], pictures: [], glyph: '3'},
    {words: ['four'], pictures: [], glyph: '4'},
    {words: ['five'], pictures: [], glyph: '5'},
    {words: ['six'], pictures: [], glyph: '6'},
    {words: ['seven'], pictures: [], glyph: '7'},
    {words: ['eight'], pictures: [], glyph: '8'},
    {words: ['nine'], pictures: [], glyph: '9'},

    {words: ['smile'], pictures: [], glyph: '😀'},

  ]
  const gridWidth = 6;
  const gridHeight = 5;
  const gridSize = gridWidth * gridHeight;
  const selectedWordsPairs = shuffle(wordsPairs).slice(0, Math.floor(gridSize / 2));  // 8 words
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
  const grid = chunks(cards, gridWidth);

  return (
    <div className="App">
      {
        grid.map((row, i) => (
          <div className="row" key={i}>
            {
              row.map((card) => (
                <Card
                  card={card}
                  key={card.id}
                  className={`${card.selected ? 'selected' : ''} ${card.hidden ? 'hidden' : ''} ${card.shake ? 'shake' : ''} ${card.src.props?.className || ''}`}
                  style={card.src.props?.css||{}}
                  onClick={() => {
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
              ))
            }
          </div>
        ))
      }
    </div>
  );
}

export default App;
