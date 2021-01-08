it('should create a modal', function(){
    expect(makeModal(1)).toHaveClass('modal');
});

it('should give accurate tally on reviews', function(){
    const button = document.createElement('button')
    button.classList.add('likeReview')
    document.body.append(button)
    let tally = document.createElement('p')
    tally.classList.add('numlikes')
    document.body.append(tally)
    handleReviewUpvote()
    expect(tally.innerText).toEqual('1')
    handleReviewUnUpvote()
    expect(tally.innerText).toEqual('0')
    button.remove()
    tally.remove()
})

it('should give accurate tally on answers', function(){
    const p = document.createElement('p')
    p.id = 1
    document.body.append(p)
    const button = document.createElement('button')
    button.classList.add('likeAnswer')
    p.append(button)
    let tally = document.createElement('p')
    tally.classList.add('tally')
    p.append(tally)
    handleAnswerUpvote(1)
    expect(tally.innerText).toEqual('1')
    handleAnswerUnUpvote(1)
    expect(tally.innerText).toEqual('0')
    p.remove()
    button.remove()
    tally.remove()
})

it('should display and remove answer edit box', function(){
    const ans = document.createElement('form')
    ans.id ='q_answer'
    document.body.append(ans)
    const p = document.createElement('div')
    p.id = 1
    document.body.append(p)
    const text = document.createElement('p')
    text.classList.add('answer')
    p.append(text)
    displayAnswerEdit(1)
    expect(ans).toHaveClass('hidden')
    expect(text).toHaveClass('hidden')
    removeAnswerEdit(1)
    expect(ans).not.toHaveClass('hidden')
    expect(text).not.toHaveClass('hidden')
    ans.remove()
    p.remove()
    text.remove()
})