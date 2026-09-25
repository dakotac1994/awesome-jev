// Jev quickstart in TypeScript. Needs TYPESAFE_API_KEY in the environment.
//
// Usage:
//   npm install @typesafe-ai/sdk
//   TYPESAFE_API_KEY=ts_... node js/quickstart.mjs
import { TypeSafeClient, Choice, Noul, Score } from '@typesafe-ai/sdk';

const client = new TypeSafeClient({ apiKey: process.env.TYPESAFE_API_KEY });

const result = await client.systemOne({
  state:
    "Hi, I've been trying to connect my Stripe account for 3 days " +
    "and it keeps failing. I'm losing sales. Please help ASAP.",
  questions: {
    department: Choice({
      instructions: 'Which team should handle this',
      criteria: {
        billing: 'Payment or subscription issues',
        technical: 'Bugs or integration problems',
        sales: 'Pricing or account questions',
      },
    }),
    frustration: Score({
      instructions: 'How frustrated the customer appears',
      criteria: ['Calm, just stating facts', 'Frustrated but civil', 'Very angry, strong language'],
    }),
    isUrgent: Noul({ instructions: 'The message conveys urgency or time-sensitivity' }),
  },
});

console.log('department :', result.answers.department.choice);
console.log('frustration:', result.answers.frustration.score);
console.log('isUrgent   :', result.answers.isUrgent.noul);
