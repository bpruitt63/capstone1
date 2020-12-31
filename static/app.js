
/// Answer a question about a game
document.body.addEventListener('submit', function(e){
    if (e.target.id === 'q_answer'){
        e.preventDefault()
        const ans = document.querySelector('#answer')
        const answer = ans.value
        if (answer === ''){
            alert("Answer cannot be blank")
            return false;
        }
        else{
            ans.value = ''
            const question_id = document.querySelector('#question_id').value
            submitAnswer(answer, question_id)
        }
    }
})

async function submitAnswer(answer, question_id){
    const resp = await axios({
        method: "POST",
        url: `/questions/${question_id}/answer`,
        data: {
            "text": answer
        }
    })
    handleAnswer(resp)
}

function handleAnswer(resp){
    const newAnswer = document.createElement('p')
    const text = resp.data.text
    const user = resp.data.username
    const timestamp = resp.data.timestamp
    newAnswer.id = resp.data.answer_id
    newAnswer.innerHTML = `<a href="/users/${user}">${user}</a>
                            <span>${timestamp}</span>
                            <span class='answer'>${text}</span> 
                            <button class='editAnswer'>Edit Answer</button>`
    const answers = document.querySelector('#answerlist')
    answers.append(newAnswer)
}


/// Edit an answer
document.body.addEventListener('click', function(e){
    if (e.target.classList.contains('editAnswer')){
        const answer_id = e.target.parentElement.id
        displayAnswerEdit(answer_id)
    }
})

function displayAnswerEdit(answer_id){
    const ans = document.querySelector('#q_answer')
    const p = document.getElementById(`${answer_id}`)
    const text = p.querySelector('.answer')
    ans.classList.add('hidden')
    text.classList.add('hidden')
    const editButtons = document.getElementsByClassName('editAnswer')
        for (button of editButtons){
            button.classList.add('hidden')
        }
    const likeButtons = document.getElementsByClassName('likeAnswer')
        for (button of likeButtons){
            button.classList.add('hidden')
        }
    const unlikeButtons = document.getElementsByClassName('unlikeAnswer')
        for (button of unlikeButtons){
            button.classList.add('hidden')
        }
    const box = document.createElement('textarea')
    box.value = text.innerText
    box.classList.add('box')
    const save = document.createElement('button')
    save.innerText = "Save"
    save.classList.add('save')
    const cancel = document.createElement('button')
    cancel.innerText = "Cancel"
    cancel.classList.add('cancel')
    const dlt = document.createElement('button')
    dlt.innerText = "Delete Answer"
    dlt.classList.add('dlt')
    p.append(box)
    p.append(save)
    p.append(cancel)
    p.append(dlt)
}

document.body.addEventListener('click', function(e){
    if (e.target.classList.contains('cancel')){
        const answer_id = e.target.parentElement.id
        removeAnswerEdit(answer_id)
    }
})

document.body.addEventListener('click', function(e){
    if (e.target.classList.contains('save')){
        const answer_id = e.target.parentElement.id
        saveAnswerEdit(answer_id)
    }
})

async function saveAnswerEdit(answer_id){
    const p = document.getElementById(`${answer_id}`)
    const textarea = p.querySelector('.box')
    const text = textarea.value
    if (text === ''){
        alert("Answer cannot be blank")
        return false;
    }
    else{
        const resp = await axios({
            method: "PATCH",
            url: `/answers/${answer_id}/edit`,
            data: {
                "text": text
            }
        })
        const span = p.querySelector('.answer')
        span.innerText = resp.data.text
        const newTarget = document.querySelector('.cancel')
        removeAnswerEdit(answer_id)
    }
}

function removeAnswerEdit(answer_id){
    const p = document.getElementById(`${answer_id}`)
    p.querySelector('.box').remove()
    p.querySelector('.save').remove()
    p.querySelector('.cancel').remove()
    p.querySelector('.dlt').remove()
    const text = p.querySelector('.answer')
    const ans = document.querySelector('#q_answer')
    text.classList.remove('hidden')
    ans.classList.remove('hidden')
    const editButtons = document.getElementsByClassName('editAnswer')
        for (button of editButtons){
            button.classList.remove('hidden')
        }
    const likeButtons = document.getElementsByClassName('likeAnswer')
        for (button of likeButtons){
            button.classList.remove('hidden')
        }
    const unlikeButtons = document.getElementsByClassName('unlikeAnswer')
        for (button of unlikeButtons){
            button.classList.remove('hidden')
        }
}


/// Delete an answer
document.body.addEventListener('click', function(e){
    if (e.target.classList.contains('dlt')){
        const answer_id = e.target.parentElement.id
        if (confirm('Are you sure you want to delete this answer?')){
            deleteAnswer(answer_id)
        }
    }
})

async function deleteAnswer(answer_id){
    const p = document.getElementById(`${answer_id}`)
    const resp = await axios({
        method: "DELETE",
        url: `/answers/${answer_id}/delete`
    })
    removeAnswerEdit(answer_id)
    p.remove()
}

/// Like or unlike a review
document.body.addEventListener('click', function(e){
    if (e.target.classList.contains('likeReview')){
        const review_id = e.target.id
        upvoteReview(review_id)
    }
    if (e.target.classList.contains('unlikeReview')){
        const review_id = e.target.id
        unUpvoteReview(review_id)
    }
})

async function upvoteReview(review_id){
    const resp = await axios({
        method: "POST",
        url: `/reviews/${review_id}/upvote`
    })
    handleReviewUpvote()
}

function handleReviewUpvote(){
    const button = document.querySelector('.likeReview')
    const tally = document.querySelector('.numlikes')
    button.innerText = 'Unlike'
    button.classList.remove('likeReview')
    button.classList.add('unlikeReview')
    tally.innerText ++
}

async function unUpvoteReview(review_id){
    const resp = await axios({
        method: "DELETE",
        url: `/reviews/${review_id}/remove_upvote`
    })
    handleReviewUnUpvote()
}

function handleReviewUnUpvote(){
    const button = document.querySelector('.unlikeReview')
    const tally = document.querySelector('.numlikes')
    button.innerText = 'Like'
    button.classList.remove('unlikeReview')
    button.classList.add('likeReview')
    tally.innerText --
}


/// Like or unlike an answer
document.body.addEventListener('click', function(e){
    if (e.target.classList.contains('likeAnswer')){
        const answer_id = e.target.parentElement.id
        upvoteAnswer(answer_id)
    }
    if (e.target.classList.contains('unlikeAnswer')){
        const answer_id = e.target.parentElement.id
        unUpvoteAnswer(answer_id)
    }
})

async function upvoteAnswer(answer_id){
    const resp = await axios({
        method: "POST",
        url: `/answers/${answer_id}/upvote`
    })
    handleAnswerUpvote(answer_id)
}

function handleAnswerUpvote(answer_id){
    const p = document.getElementById(`${answer_id}`)
    const button = p.querySelector('button')
    button.innerText = 'Unlike'
    button.classList.remove('likeAnswer')
    button.classList.add('unlikeAnswer')
    tally = p.querySelector('.tally')
    tally.innerText ++
}

async function unUpvoteAnswer(answer_id){
    const resp = await axios({
        method: "DELETE",
        url: `/answers/${answer_id}/remove_upvote`
    })
    handleAnswerUnUpvote(answer_id)
}

function handleAnswerUnUpvote(answer_id){
    const p = document.getElementById(`${answer_id}`)
    const button = p.querySelector('.unlikeAnswer')
    button.innerText = 'Like'
    button.classList.remove('unlikeAnswer')
    button.classList.add('likeAnswer')
    tally = p.querySelector('.tally')
    tally.innerText --
}


/// Delete a question
document.body.addEventListener('click', function(e){
    if (e.target.classList.contains('deletequestion')){
        const question_id = e.target.id
        if (confirm('Are you sure you want to delete this question?')){
            deleteQuestion(question_id)
        }
    }
})

async function deleteQuestion(question_id){
    const resp = await axios({
        method: "DELETE",
        url: `/questions/${question_id}/delete`
    })
    const game_id = resp.data.game_id
    window.open(`/games/${game_id}/questions`, '_self')
}


/// Delete a review
document.body.addEventListener('click', function(e){
    if (e.target.classList.contains('deletereview')){
        const review_id = e.target.id
        if (confirm('Are you sure you want to delete this review?')){
            deleteReview(review_id)
        }
    }
})

async function deleteReview(review_id){
    const resp = await axios({
        method: "DELETE",
        url: `/reviews/${review_id}/delete`
    })
    const game_id = resp.data.game_id
    window.open(`/games/${game_id}/reviews`, '_self')
}