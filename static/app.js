
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
    const user = resp.data.username
    const newAnswer = document.createElement('div')
    newAnswer.classList.add('row', 'qans')
    newAnswer.id = resp.data.answer_id
    const newInfo = document.createElement('div')
    newInfo.classList.add('col-sm-8')
    const userLink = document.createElement('a')
    userLink.href = `/users/${user}`
    userLink.innerText = `${user}`
    const br = document.createElement("BR")
    const br2 = document.createElement("BR")
    const time = document.createElement('span')
    time.innerText = resp.data.timestamp
    newInfo.append(userLink)
    newInfo.append(br)
    newInfo.append(time)
    newAnswer.append(newInfo)
    const newText = document.createElement('div')
    newText.classList.add('col-12')
    newText.append(br2)
    const ansText = document.createElement('p')
    ansText.classList.add('answer')
    ansText.innerText = resp.data.text
    newText.append(ansText)
    const newEdit = document.createElement('button')
    newEdit.classList.add('editAnswer', 'btn', 'btn-sm', 'btn-secondary')
    newEdit.innerText = 'Edit Answer'
    newText.append(newEdit)
    newAnswer.append(newText)    
    const answers = document.querySelector('#answerlist')
    answers.append(newAnswer)
}


/// Edit an answer
document.body.addEventListener('click', function(e){
    if (e.target.classList.contains('editAnswer')){
        const answer_id = e.target.parentElement.parentElement.id
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
    box.classList.add('box', 'form-control')
    const save = document.createElement('button')
    save.innerText = "Save"
    save.classList.add('save', 'btn', 'btn-secondary')
    const cancel = document.createElement('button')
    cancel.innerText = "Cancel"
    cancel.classList.add('cancel', 'btn', 'btn-light')
    const dlt = document.createElement('button')
    dlt.innerText = "Delete Answer"
    dlt.classList.add('dlt', 'btn', 'btn-dark')
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
    if (e.target.parentElement.classList.contains('likeReview')){
        const review_id = e.target.parentElement.id
        upvoteReview(review_id)
    }
    if (e.target.classList.contains('unlikeReview')){
        const review_id = e.target.id
        unUpvoteReview(review_id)
    }
    if (e.target.parentElement.classList.contains('unlikeReview')){
        const review_id = e.target.parentElement.id
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
    button.innerHTML = "<img src='/static/images/unlike.png' alt='Dislike' class='likeimg'>"
    button.classList.remove('likeReview', 'btn-outline-success')
    button.classList.add('unlikeReview', 'btn-outline-danger')
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
    button.innerHTML = "<img src='/static/images/like.png' alt='Like' class='likeimg'>"
    button.classList.remove('unlikeReview', 'btn-outline-danger')
    button.classList.add('likeReview', 'btn-outline-success')
    tally.innerText --
}


/// Like or unlike an answer
document.body.addEventListener('click', function(e){
    if (e.target.classList.contains('likeAnswer')){
        const answer_id = e.target.parentElement.parentElement.parentElement.id
        upvoteAnswer(answer_id)
    }
    if (e.target.parentElement.classList.contains('likeAnswer')){
        const answer_id = e.target.parentElement.parentElement.parentElement.parentElement.id
        upvoteAnswer(answer_id)
    }
    if (e.target.classList.contains('unlikeAnswer')){
        const answer_id = e.target.parentElement.parentElement.parentElement.id
        unUpvoteAnswer(answer_id)
    }
    if (e.target.parentElement.classList.contains('unlikeAnswer')){
        const answer_id = e.target.parentElement.parentElement.parentElement.parentElement.id
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
    const button = p.querySelector('.likeAnswer')
    button.classList.remove('likeAnswer', 'btn-outline-success')
    button.classList.add('unlikeAnswer', 'btn-outline-danger')
    button.innerHTML = "<img src='/static/images/unlike.png' alt='Dislike' class='likeimg'>"
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
    button.classList.remove('unlikeAnswer', 'btn-outline-danger')
    button.classList.add('likeAnswer', 'btn-outline-success')
    button.innerHTML = "<img src='/static/images/like.png' alt='Like' class='likeimg'>"
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