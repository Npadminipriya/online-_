from models import db, app
from models import Election, Candidate


with app.app_context():
    # Create a sample election
    election = Election(
        title="National General Elections",
        description="Vote for the next leader of the country.",
        image_url="https://northeastlive.s3.amazonaws.com/media/uploads/2019/04/general-elections-2019-m_660_042919091753.jpg"
    )
    db.session.add(election)
    db.session.commit()

    # Add sample candidates
    candidates = [
        Candidate(name="Alice Johnson", party="Party A", votes=10, election_id=election.id),
        Candidate(name="Bob Smith", party="Party B", votes=15, election_id=election.id),
        Candidate(name="Charlie Davis", party="Party C", votes=5, election_id=election.id)
    ]

    db.session.add_all(candidates)
    db.session.commit()

    print("Sample election and candidates added successfully!")
