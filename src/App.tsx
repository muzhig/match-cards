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


function App() {
  const wordsPairs = [
    {word: 'cat', picture: '/img/cat.png'},
    {word: 'dog', picture: '/img/dog.png'},
    {word: 'ball', picture: '/img/ball.png'},
    {word: 'eraser', picture: '/img/eraser.png'},
    {word: 'toys', picture: '/img/toys.png'},
    {word: 'rocket', picture: '/img/rocket.png'},
    {word: 'pencil', picture: '/img/pencil.png'},
    {word: 'book', picture: '/img/book.png'},
  ]
  const cardDefs = wordsPairs.map((pair, i) => [
    {id: `word-${i}`, word: pair.word, picture: undefined},
    {id: `pic-${i}`, word: pair.word, picture: pair.picture},
  ]);
  const cardsArray: Array<CardState> = cardDefs[0].concat(...cardDefs.slice(1)).map((card, i) => (
    {
      ...card,
      order: i,
    }
  ));
  // shuffled
  const [cards, setCards] = useState(cardsArray.sort(() => Math.random() - 0.5));
  const [selected, setSelected] = useState<CardState | undefined>(undefined);
  const grid = []
  const rowSize = 4
  for (let i = 0; i < cards.length; i += rowSize) {
    grid.push(cards.slice(i, i + rowSize))
  }
  const speak = (word: string) => {
    const voices = speechSynthesis.getVoices();
    const voice = voices.find((v) => v.name === 'Google US English');
    const utterance = new SpeechSynthesisUtterance(word);
    utterance.voice = voice || null;
    utterance.pitch = 1.0 + Math.random() * 0.2;
    utterance.rate = 0.7 + Math.random() * 0.3;


    speechSynthesis.speak(utterance);
  };
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
                  className={`${card.selected ? 'selected' : ''} ${card.hidden ? 'hidden' : ''} ${card.shake ? 'shake' : ''}`}

                  onClick={() => {
                    if (selected && selected.id !== card.id) {
                      if (selected.word === card.word) {
                        // match
                        // play sound effect
                        // fade out cards from the board
                        speak("Awesome!");
                        setSelected(undefined)
                        setCards(cards.map((c) => {
                          if (c.id === selected.id || c.id === card.id) {
                            return {...c, selected: false, hidden: true}
                          }
                          return c
                        }))
                      } else {
                        if(!card.picture) {
                          speak(card.word)
                        }
                        // no match
                        // add .shake class for 1 second
                        // remove .shake class
                        speak("No!")
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
                        if (card.selected && card.picture === undefined) {
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
